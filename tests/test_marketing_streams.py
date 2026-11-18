"""Tests for the marketing streams, against a fake HubSpot API."""

from __future__ import annotations

import io
import json
import typing as t
from contextlib import redirect_stdout
from urllib.parse import parse_qs, urlparse

import pytest
import requests

from tap_hubspot import client, streams
from tap_hubspot import marketing_streams as ms
from tap_hubspot.client import DAILY_REMAINING_HEADER
from tap_hubspot.tap import TapHubspot

DAY = ms.DAY_MS
# 2026-11-10T00:00:00Z
T0 = 1794268800000
LISTS_SEARCH_PATH = f"/crm/lists/{client.API_VERSION}/search"


class FakeHubSpot:
    """Answers the requests of the marketing streams and records each request."""

    def __init__(self) -> None:
        """Start with no data."""
        self.events: list[dict] = []
        self.forms: list[dict] = []
        self.submissions: dict[str, list[dict]] = {}
        self.campaign_ids: list[int] = []
        self.lists: list[dict] = []
        self.calls: list[tuple[str, dict]] = []
        self.fail_on_window_start: int | None = None
        self.page_size = 2
        self.daily_remaining: int | None = None

    def send(self, request: requests.PreparedRequest, **_: t.Any) -> requests.Response:
        """Return the response for a request, as `requests.Session.send` does."""
        url = urlparse(t.cast("str", request.url))
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        if request.body:
            query.update(json.loads(request.body))
        self.calls.append((url.path, query))
        body = self._route(url.path, query)
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps(body).encode()  # noqa: SLF001
        response.request = request
        if self.daily_remaining is not None:
            response.headers[DAILY_REMAINING_HEADER] = str(self.daily_remaining)
        return response

    def _page(self, rows: list, offset: int) -> tuple[list, bool]:
        page = rows[offset : offset + self.page_size]
        return page, offset + self.page_size < len(rows)

    def _route(self, path: str, query: dict) -> dict | list:
        offset = int(query.get("offset", 0))
        if path == "/email/public/v1/events":
            start, end = int(query["startTimestamp"]), int(query["endTimestamp"])
            if start == self.fail_on_window_start:
                raise requests.exceptions.ConnectionError("fake outage")  # noqa: EM101, TRY003
            rows = sorted(
                (e for e in self.events if start <= e["created"] < end),
                key=lambda e: e["created"],
                reverse=True,
            )
            page, more = self._page(rows, offset)
            return {"events": page, "hasMore": more, "offset": offset + len(page)}
        if path == "/forms/v2/forms":
            return self.forms
        if path.startswith("/form-integrations/v1/submissions/forms/"):
            form_id = path.rsplit("/", 1)[1]
            rows = self.submissions[form_id]
            after = int(query.get("after", 0))
            page, more = self._page(rows, after)
            paging = {"next": {"after": str(after + len(page))}} if more else None
            return {"results": page, **({"paging": paging} if paging else {})}
        if path == "/email/public/v1/campaigns/by-id":
            ids = [{"id": i} for i in self.campaign_ids]
            page, more = self._page(ids, offset)
            return {"campaigns": page, "hasMore": more, "offset": offset + len(page)}
        if path.startswith("/email/public/v1/campaigns/"):
            campaign_id = int(path.rsplit("/", 1)[1])
            return {
                "id": campaign_id,
                "name": f"c{campaign_id}",
                "counters": {"sent": 3},
            }
        if path == LISTS_SEARCH_PATH:
            page, more = self._page(self.lists, offset)
            return {"lists": page, "hasMore": more, "offset": offset + len(page)}
        raise AssertionError(path)


@pytest.fixture
def fake(monkeypatch: pytest.MonkeyPatch) -> FakeHubSpot:
    """Send all HTTP requests of the test to a fake HubSpot API."""
    api = FakeHubSpot()
    monkeypatch.setattr(
        requests.Session,
        "send",
        lambda _, req, **kw: api.send(req, **kw),
    )
    monkeypatch.setattr(ms.TimeWindowStream, "page_size", api.page_size)
    monkeypatch.setattr(ms.HubspotStream, "backoff_max_tries", lambda _: 1)
    return api


def run_tap(
    stream_classes: list[type],
    *,
    state: dict | None = None,
    expect_error: bool = False,
    config: dict | None = None,
) -> tuple[list[dict], list[dict]]:
    """Sync the given streams and return (records, states) from the Singer output."""

    class Tap(TapHubspot):
        def discover_streams(self) -> list:
            return [cls(self) for cls in stream_classes]

    tap = Tap(
        config={"access_token": "x", "start_date": ms.ms_to_iso(T0), **(config or {})},
        state=state or {},
        setup_mapper=True,
    )
    out = io.StringIO()
    with redirect_stdout(out):
        if expect_error:
            with pytest.raises(Exception):  # noqa: B017, PT011
                tap.sync_all()
        else:
            tap.sync_all()
    messages = [json.loads(line) for line in out.getvalue().splitlines() if line]
    records = [m for m in messages if m["type"] == "RECORD"]
    states = [m["value"] for m in messages if m["type"] == "STATE"]
    return records, states


def bookmark(state: dict, stream: str) -> str | None:
    """Return the bookmark of a stream that keeps a single state entry."""
    return state["bookmarks"].get(stream, {}).get("replication_key_value")


def test_email_events_bookmark_moves_after_each_window(fake: FakeHubSpot) -> None:
    """An interrupted sync continues from the last complete day."""
    # Three events in each of the first three days.
    fake.events = [
        {"id": f"{d}-{i}", "created": T0 + d * DAY + i * 1000, "type": "SENT"}
        for d in range(3)
        for i in range(3)
    ]
    fake.fail_on_window_start = T0 + 2 * DAY

    records, states = run_tap([ms.EmailEventsStream], expect_error=True)

    assert {r["record"]["id"] for r in records} == {
        f"{d}-{i}" for d in range(2) for i in range(3)
    }
    # The last state before the failure keeps the newest event of day 1.
    assert bookmark(states[-1], "email_events") == ms.ms_to_iso(T0 + DAY + 2000)

    fake.fail_on_window_start = None
    records, _ = run_tap([ms.EmailEventsStream], state=states[-1])

    ids = sorted(r["record"]["id"] for r in records)
    # The resumed sync starts at the bookmark, so only the bookmark event repeats.
    assert ids == ["1-2", "2-0", "2-1", "2-2"]


def test_form_submissions_stop_at_bookmark_and_skip_unexportable_forms(
    fake: FakeHubSpot,
) -> None:
    """Paging stops at the bookmark of each form and skips unexportable forms."""
    fake.forms = [
        {"guid": "f-hubspot", "formType": "HUBSPOT"},
        {"guid": "f-facebook", "formType": "FACEBOOK_LEAD_AD"},
        {"guid": "f-captured", "formType": "CAPTURED"},
    ]
    newest_first = [
        {
            "conversionId": f"s{i}",
            "submittedAt": T0 + (10 - i) * DAY,
            "pageUrl": "https://x",
        }
        for i in range(10)
    ]
    fake.submissions = {"f-hubspot": newest_first, "f-captured": newest_first[:1]}
    # The HubSpot form already has everything up to s3 (T0 + 7 days).
    state = {
        "bookmarks": {
            "form_submissions": {
                "partitions": [
                    {
                        "context": {"formId": "f-hubspot"},
                        "replication_key": "submittedAt",
                        "replication_key_value": ms.ms_to_iso(T0 + 7 * DAY),
                    },
                ],
            },
        },
    }

    records, _ = run_tap([ms.FormsStream, ms.FormSubmissionsStream], state=state)

    submissions = [r["record"] for r in records if r["stream"] == "form_submissions"]
    by_form = {
        form: [s["conversionId"] for s in submissions if s["formId"] == form]
        for form in ("f-hubspot", "f-captured")
    }
    assert by_form == {"f-hubspot": ["s0", "s1", "s2", "s3"], "f-captured": ["s0"]}
    assert all(s["pageUrl"] == "https://x" for s in submissions)
    paths = [path for path, _ in fake.calls]
    assert "/form-integrations/v1/submissions/forms/f-facebook" not in paths
    # Pages of 2: s0-s1, s2-s3, then s4-s5 reaches the bookmark and paging stops.
    assert paths.count("/form-integrations/v1/submissions/forms/f-hubspot") == 3


def test_campaigns_read_each_campaign_with_one_state_entry(fake: FakeHubSpot) -> None:
    """Campaign details keep one state entry, not one per campaign."""
    fake.campaign_ids = [11, 12, 13]

    records, states = run_tap([ms.CampaignIdsStream, ms.CampaignsStream])

    campaigns = [r["record"] for r in records if r["stream"] == "campaigns"]
    assert [c["id"] for c in campaigns] == [11, 12, 13]
    assert campaigns[0]["counters"] == {"sent": 3}
    assert "partitions" not in states[-1]["bookmarks"].get("campaigns", {})


def test_contact_lists_page_with_offset(fake: FakeHubSpot) -> None:
    """The lists search pages with the offset of the previous response."""
    fake.lists = [{"listId": str(i), "name": f"l{i}"} for i in range(5)]

    records, _ = run_tap([ms.ContactListsStream])

    assert [r["record"]["listId"] for r in records] == ["0", "1", "2", "3", "4"]
    offsets = [q["offset"] for path, q in fake.calls if path == LISTS_SEARCH_PATH]
    assert offsets == [0, 2, 4]


def test_sync_stops_below_daily_request_reserve(fake: FakeHubSpot) -> None:
    """The sync stops after the first response below the daily reserve."""
    fake.lists = [{"listId": str(i), "name": f"l{i}"} for i in range(5)]
    fake.daily_remaining = 999

    records, _ = run_tap(
        [ms.ContactListsStream],
        expect_error=True,
        config={"daily_request_reserve": 1000},
    )

    assert records == []
    assert len(fake.calls) == 1


def test_throttle_spaces_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Requests are spaced by 1 / max_requests_per_second."""
    clock = {"now": 100.0}
    sleeps: list[float] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock["now"] += seconds

    monkeypatch.setattr(client.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(client.time, "sleep", sleep)
    throttle = client.RequestThrottle()

    for _ in range(3):
        throttle.wait(4)

    assert sleeps == [0.25, 0.25]


def test_crm_streams_use_date_based_urls() -> None:
    """The CRM streams call the date-based API version."""

    class Tap(TapHubspot):
        def discover_streams(self) -> list:
            return []

    tap = Tap(config={"access_token": "x"}, setup_mapper=False)
    base = "https://api.hubapi.com/crm"
    version = client.API_VERSION

    assert streams.OwnersStream(tap).get_url(None) == f"{base}/owners/{version}"
    properties = client.PropertyStream(tap, "contacts")
    assert properties.get_url(None) == f"{base}/properties/{version}/contacts"
    ids = client.IdOnlyObjectStream(tap, "deals")
    assert ids.get_url(None) == f"{base}/objects/{version}/deals"
    assert streams.ContactStream.incremental_path == "/contacts/search"
