"""Tests for the events stream."""
# ruff: noqa: S101

from __future__ import annotations

import typing as t
from unittest import mock

from singer_sdk.helpers._flattening import flatten_schema

from tap_hubspot.streams import EventStream
from tap_hubspot.tap import TapHubspot

CONFIG = {
    "access_token": "token",
    "start_date": "2024-01-01T00:00:00Z",
    "event_types": ["e_visited_page", "e_submitted_form"],
}


def _stream() -> EventStream:
    # Discovery reads every dynamic stream's properties from the API, which a
    # unit test has no credentials for.
    with mock.patch.object(TapHubspot, "discover_streams", return_value=[]):
        return EventStream(TapHubspot(config=CONFIG, parse_env_config=False))


def test_one_partition_per_event_type() -> None:
    """Each configured event type gets its own partition."""
    assert _stream().partitions == [
        {"eventType": "e_visited_page"},
        {"eventType": "e_submitted_form"},
    ]


def test_url_params_filter_by_type_and_start_date() -> None:
    """Params carry the partition's type and its bookmark, and omit `sort`."""
    stream = _stream()
    context = {"eventType": "e_visited_page"}
    # A sync seeds each partition's bookmark before its first request.
    stream._write_starting_replication_value(context)  # noqa: SLF001
    params = stream.get_url_params(context, None)
    assert params["eventType"] == "e_visited_page"
    assert params["occurredAfter"] == "2024-01-01T00:00:00+00:00"
    # The endpoint rejects `sort`, which the inherited params would have set.
    assert "sort" not in params


def test_url_params_page_forward() -> None:
    """A page token is passed through as `after`."""
    page_cursor: t.Any = "page-2"
    params = _stream().get_url_params({"eventType": "e_visited_page"}, page_cursor)
    assert params["after"] == "page-2"


def test_properties_survive_flattening() -> None:
    """Flattening keeps `properties` whole rather than expanding it away."""
    flat = flatten_schema(EventStream.schema, max_level=1)
    assert "properties" in flat["properties"]
