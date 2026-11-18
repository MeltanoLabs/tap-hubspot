"""Streams for the HubSpot marketing APIs: email events, campaigns, forms and lists.

Most of these endpoints are legacy v1 APIs that have no v3 replacement.
"""

from __future__ import annotations

import datetime
import sys
import typing as t

from singer_sdk import typing as th
from singer_sdk.streams.core import REPLICATION_INCREMENTAL

from tap_hubspot.client import HubspotStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context, Record

DAY_MS = 24 * 60 * 60 * 1000

# The submissions API returns HTTP 400 "Submissions can't be exported for this form"
# for these form types.
UNEXPORTABLE_FORM_TYPES = frozenset(
    {"FACEBOOK_LEAD_AD", "MEETING", "DOCUMENT", "BLOG_COMMENT"},
)


def ms_to_iso(value: int | None) -> str | None:
    """Convert epoch milliseconds to an ISO 8601 UTC timestamp.

    The fixed millisecond precision keeps bookmark values comparable as strings.
    """
    if value is None:
        return None
    return datetime.datetime.fromtimestamp(
        value / 1000,
        tz=datetime.timezone.utc,
    ).isoformat(timespec="milliseconds")


def to_ms(value: datetime.datetime) -> int:
    """Convert a datetime to epoch milliseconds."""
    return int(value.timestamp() * 1000)


class LegacyEmailStream(HubspotStream):
    """Base for the legacy email APIs, which page with `offset` and `hasMore`."""

    @override
    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com/email/public/v1"

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any,
    ) -> t.Any:
        data = response.json()
        return data.get("offset") if data.get("hasMore") else None


class TimeWindowStream(LegacyEmailStream):
    """Reads the API one time window at a time, from old to new.

    The API returns each window newest first, so the stream is not sorted. The
    bookmark moves at the end of each window: an interrupted sync continues from
    the last complete window instead of from the start of the sync.
    """

    replication_method = REPLICATION_INCREMENTAL
    is_sorted = False
    window_ms = DAY_MS
    page_size = 1000

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:  # noqa: D107
        super().__init__(*args, **kwargs)
        self._window = (0, 0)

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {
            "startTimestamp": self._window[0],
            "endTimestamp": self._window[1],
            "limit": self.page_size,
        }
        if next_page_token:
            params["offset"] = next_page_token
        return params

    @override
    def request_records(self, context: Context | None) -> t.Iterable[dict]:
        start = self.get_starting_timestamp(context)
        if start is None:
            msg = f"Stream '{self.name}' needs a start_date or a bookmark."
            raise ValueError(msg)
        start_ms = to_ms(start)
        end_ms = to_ms(datetime.datetime.now(datetime.timezone.utc))
        while start_ms < end_ms:
            self._window = (start_ms, min(start_ms + self.window_ms, end_ms))
            yield from super().request_records(context)
            # All records of the window are processed when the generator resumes.
            self.finalize_state_progress_markers(self.get_context_state(context))
            start_ms = self._window[1]

    @override
    def post_process(self, row: Record, context: Context | None = None) -> Record:
        key = t.cast("str", self.replication_key)
        row[key] = ms_to_iso(row.get(key))
        return row


class EmailEventsStream(TimeWindowStream):
    """https://legacydocs.hubspot.com/docs/methods/email/get_events.

    Nested timestamps (`causedBy.created`, `sentBy.created`, ...) stay in epoch
    milliseconds, as the API sends them.
    """

    name = "email_events"
    path = "/events"
    primary_keys = ("id",)
    replication_key = "created"
    records_jsonpath = "$.events[*]"

    _reference = th.ObjectType(
        th.Property("id", th.StringType),
        th.Property("created", th.IntegerType),
    )

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("type", th.StringType),
        th.Property("recipient", th.StringType),
        th.Property("emailCampaignId", th.IntegerType),
        th.Property("emailCampaignGroupId", th.IntegerType),
        th.Property("portalId", th.IntegerType),
        th.Property("appId", th.IntegerType),
        th.Property("appName", th.StringType),
        th.Property("sentBy", _reference),
        th.Property("causedBy", _reference),
        th.Property("obsoletedBy", _reference),
        th.Property("filteredEvent", th.BooleanType),
        th.Property("smtpId", th.StringType),
        th.Property("hmid", th.StringType),
        th.Property("subject", th.StringType),
        th.Property("from", th.StringType),
        th.Property("replyTo", th.ArrayType(th.StringType)),
        th.Property("cc", th.ArrayType(th.StringType)),
        th.Property("bcc", th.ArrayType(th.StringType)),
        th.Property("response", th.StringType),
        th.Property("attempt", th.IntegerType),
        th.Property("status", th.StringType),
        th.Property("category", th.StringType),
        th.Property("bounced", th.BooleanType),
        th.Property("impactedByGlobalBounce", th.BooleanType),
        th.Property("dropReason", th.StringType),
        th.Property("dropMessage", th.StringType),
        th.Property("suppressedReason", th.StringType),
        th.Property("suppressedMessage", th.StringType),
        th.Property("franklinResponseType", th.StringType),
        th.Property("url", th.StringType),
        th.Property("linkId", th.IntegerType),
        th.Property("linkIdV2", th.StringType),
        th.Property("referer", th.StringType),
        th.Property("userAgent", th.StringType),
        th.Property("ipAddress", th.StringType),
        th.Property("deviceType", th.StringType),
        th.Property("duration", th.IntegerType),
        th.Property(
            "browser",
            th.ObjectType(
                th.Property("name", th.StringType),
                th.Property("family", th.StringType),
                th.Property("producer", th.StringType),
                th.Property("producerUrl", th.StringType),
                th.Property("type", th.StringType),
                th.Property("url", th.StringType),
                th.Property("version", th.ArrayType(th.StringType)),
            ),
        ),
        th.Property(
            "location",
            th.ObjectType(
                th.Property("city", th.StringType),
                th.Property("state", th.StringType),
                th.Property("country", th.StringType),
                th.Property("zipcode", th.StringType),
                th.Property("latitude", th.NumberType),
                th.Property("longitude", th.NumberType),
            ),
        ),
        th.Property("source", th.StringType),
        th.Property("sourceId", th.StringType),
        th.Property("portalSubscriptionStatus", th.StringType),
        th.Property("requestedBy", th.StringType),
        th.Property("requestedByUserId", th.IntegerType),
        th.Property("user", th.StringType),
        th.Property(
            "subscriptions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("status", th.StringType),
                    th.Property(
                        "legalBasisChange",
                        th.ObjectType(
                            th.Property("legalBasisType", th.StringType),
                            th.Property("legalBasisExplanation", th.StringType),
                            th.Property("optState", th.StringType),
                        ),
                    ),
                ),
            ),
        ),
    ).to_dict()


class SubscriptionChangesStream(TimeWindowStream):
    """https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions_timeline."""

    name = "subscription_changes"
    path = "/subscriptions/timeline"
    primary_keys = ("timestamp", "portalId", "recipient")
    replication_key = "timestamp"
    records_jsonpath = "$.timeline[*]"

    schema = th.PropertiesList(
        th.Property("timestamp", th.DateTimeType),
        th.Property("portalId", th.IntegerType),
        th.Property("recipient", th.StringType),
        th.Property("normalizedEmailId", th.StringType),
        th.Property(
            "changes",
            th.ArrayType(
                th.ObjectType(
                    th.Property("timestamp", th.IntegerType),
                    th.Property("portalId", th.IntegerType),
                    th.Property("subscriptionId", th.IntegerType),
                    th.Property("change", th.StringType),
                    th.Property("changeType", th.StringType),
                    th.Property("source", th.StringType),
                    th.Property(
                        "causedByEvent",
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("created", th.IntegerType),
                        ),
                    ),
                ),
            ),
        ),
    ).to_dict()


class CampaignIdsStream(LegacyEmailStream):
    """https://legacydocs.hubspot.com/docs/methods/email/get_campaigns_by_id.

    Parent of `campaigns`: the list endpoint returns ids only.
    """

    name = "campaign_ids"
    path = "/campaigns/by-id"
    primary_keys = ("id",)
    records_jsonpath = "$.campaigns[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("groupId", th.IntegerType),
        th.Property("appId", th.IntegerType),
        th.Property("appName", th.StringType),
        th.Property("lastUpdatedTime", th.IntegerType),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {"limit": 1000}
        if next_page_token:
            params["offset"] = next_page_token
        return params

    @override
    def get_child_context(self, record: Record, context: Context | None) -> dict:
        return {"campaign_id": record["id"]}


class CampaignsStream(LegacyEmailStream):
    """https://legacydocs.hubspot.com/docs/methods/email/get_campaign_data.

    Full table: the API has no modified date for campaigns, and the counters change
    after a send.
    """

    name = "campaigns"
    parent_stream_type = CampaignIdsStream
    path = "/campaigns/{campaign_id}"
    primary_keys = ("id",)
    records_jsonpath = "$"
    # One state entry instead of one per campaign.
    state_partitioning_keys = ()

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("groupId", th.IntegerType),
        th.Property("appId", th.IntegerType),
        th.Property("appName", th.StringType),
        th.Property("contentId", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("subject", th.StringType),
        th.Property("type", th.StringType),
        th.Property("subType", th.StringType),
        th.Property("processingState", th.StringType),
        th.Property("numIncluded", th.IntegerType),
        th.Property("numQueued", th.IntegerType),
        th.Property("scheduledAt", th.IntegerType),
        th.Property("lastProcessingStartedAt", th.IntegerType),
        th.Property("lastProcessingFinishedAt", th.IntegerType),
        th.Property("lastProcessingStateChangeAt", th.IntegerType),
        th.Property("counters", th.ObjectType(additional_properties=th.IntegerType)),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict[str, t.Any]:
        return {}


class FormsStream(HubspotStream):
    """https://legacydocs.hubspot.com/docs/methods/forms/v2/get_forms.

    Timestamps stay in epoch milliseconds, as the API sends them.
    """

    name = "forms"
    path = "/forms/v2/forms"
    primary_keys = ("guid",)
    records_jsonpath = "$[*]"

    schema = th.PropertiesList(
        th.Property("guid", th.StringType),
        th.Property("name", th.StringType),
        th.Property("formType", th.StringType),
        th.Property("portalId", th.IntegerType),
        th.Property("businessUnitId", th.IntegerType),
        th.Property("createdAt", th.IntegerType),
        th.Property("updatedAt", th.IntegerType),
        th.Property("internalUpdatedAt", th.IntegerType),
        th.Property("deletedAt", th.IntegerType),
        th.Property("publishAt", th.IntegerType),
        th.Property("unpublishAt", th.IntegerType),
        th.Property("publishedAt", th.IntegerType),
        th.Property("isPublished", th.BooleanType),
        th.Property("action", th.StringType),
        th.Property("method", th.StringType),
        th.Property("redirect", th.StringType),
        th.Property("submitText", th.StringType),
        th.Property("inlineMessage", th.StringType),
        th.Property("thankYouMessageJson", th.StringType),
        th.Property("notifyRecipients", th.StringType),
        th.Property("followUpId", th.StringType),
        th.Property("leadNurturingCampaignId", th.StringType),
        th.Property("campaignGuid", th.StringType),
        th.Property("migratedFrom", th.StringType),
        th.Property("parentId", th.IntegerType),
        th.Property("editVersion", th.IntegerType),
        th.Property("embedVersion", th.StringType),
        th.Property("captchaEnabled", th.BooleanType),
        th.Property("captchaVersion", th.StringType),
        th.Property("cloneable", th.BooleanType),
        th.Property("editable", th.BooleanType),
        th.Property("deletable", th.BooleanType),
        th.Property("enrichable", th.BooleanType),
        th.Property("createMarketableContact", th.BooleanType),
        th.Property("alwaysCreateNewCompany", th.BooleanType),
        th.Property("ignoreCurrentValues", th.BooleanType),
        th.Property("processDeal", th.BooleanType),
        th.Property("spamNotificationsEnabled", th.BooleanType),
        th.Property("spamNotificationsRecipients", th.StringType),
        th.Property("cssClass", th.StringType),
        th.Property("style", th.StringType),
        th.Property("themeName", th.StringType),
        th.Property("themeColor", th.StringType),
        th.Property("performableHtml", th.StringType),
        th.Property("portableKey", th.StringType),
        th.Property("customUid", th.StringType),
        th.Property("tmsId", th.StringType),
        th.Property("formFieldGroups", th.ArrayType(th.ObjectType())),
        th.Property(
            "metaData",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("value", th.StringType),
                ),
            ),
        ),
        th.Property("selectedExternalOptions", th.ArrayType(th.ObjectType())),
    ).to_dict()

    @override
    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com"

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict[str, t.Any]:
        # Without formTypes the API returns HUBSPOT forms only.
        return {"formTypes": "ALL"}

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any,
    ) -> t.Any:
        return None

    @override
    def generate_child_contexts(
        self,
        record: Record,
        context: Context | None,
    ) -> t.Iterable[Context | None]:
        if record.get("formType") not in UNEXPORTABLE_FORM_TYPES:
            # The SDK copies this key into each submission record.
            yield {"formId": record["guid"]}


class FormSubmissionsStream(HubspotStream):
    """https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form.

    The API returns submissions newest first, so a sync stops at the first page
    that reaches the bookmark of the form.
    """

    name = "form_submissions"
    parent_stream_type = FormsStream
    path = "/form-integrations/v1/submissions/forms/{formId}"
    primary_keys = ("conversionId",)
    replication_key = "submittedAt"
    replication_method = REPLICATION_INCREMENTAL
    is_sorted = False
    records_jsonpath = "$.results[*]"

    schema = th.PropertiesList(
        th.Property("conversionId", th.StringType),
        th.Property("formId", th.StringType),
        th.Property("submittedAt", th.DateTimeType),
        th.Property("pageUrl", th.StringType),
        th.Property(
            "values",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("value", th.StringType),
                    th.Property("objectTypeId", th.StringType),
                ),
            ),
        ),
    ).to_dict()

    @override
    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com"

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {"limit": 50}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def _start_ms(self, context: Context | None) -> int | None:
        start = self.get_starting_timestamp(context)
        return to_ms(start) if start else None

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any,
    ) -> t.Any:
        data = response.json()
        results = data.get("results") or []
        start_ms = self._start_ms(self.context)
        if start_ms is not None and results and results[-1]["submittedAt"] < start_ms:
            return None
        return data.get("paging", {}).get("next", {}).get("after")

    @override
    def post_process(
        self,
        row: Record,
        context: Context | None = None,
    ) -> Record | None:
        start_ms = self._start_ms(context)
        if start_ms is not None and row["submittedAt"] < start_ms:
            return None
        row["submittedAt"] = ms_to_iso(row["submittedAt"])
        return row


class ContactListsStream(HubspotStream):
    """https://developers.hubspot.com/docs/api-reference/crm-lists-v3/lists/post-crm-v3-lists-search.

    Lists of every object type. The search endpoint stops at 10,000 lists and
    returns HTTP 400 after that.
    """

    name = "contact_lists"
    path = "/crm/v3/lists/search"
    http_method = "POST"
    primary_keys = ("listId",)
    records_jsonpath = "$.lists[*]"

    schema = th.PropertiesList(
        th.Property("listId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("objectTypeId", th.StringType),
        th.Property("processingType", th.StringType),
        th.Property("processingStatus", th.StringType),
        th.Property("listVersion", th.IntegerType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("filtersUpdatedAt", th.DateTimeType),
        th.Property("deletedAt", th.DateTimeType),
        th.Property("createdById", th.StringType),
        th.Property("updatedById", th.StringType),
        th.Property("additionalProperties", th.ObjectType()),
    ).to_dict()

    @override
    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com"

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict[str, t.Any]:
        return {}

    @override
    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: t.Any,
    ) -> dict | None:
        return {"count": 500, "offset": next_page_token or 0}

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any,
    ) -> t.Any:
        data = response.json()
        return data.get("offset") if data.get("hasMore") else None
