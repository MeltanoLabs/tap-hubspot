"""Marketing Stream type classes for tap-hubspot."""

from __future__ import annotations

from datetime import datetime, UTC
from dateutil.relativedelta import relativedelta
import typing as t

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot.client import (
    HubspotStream,
)

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
DateType = th.DateType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType
NumberType = th.NumberType

ASSET_TYPES: list[str] = [
    "AD_CAMPAIGN",
    "BLOG_POST",
    "SOCIAL_BROADCAST",
    "WEB_INTERACTIVE",
    "CTA",
    "EXTERNAL_WEB_URL",
    "FORM",
    "LANDING_PAGE",
    "MARKETING_EMAIL",
    "MARKETING_EVENT",
    "OBJECT_LIST",
    "SITE_PAGE",
    "AUTOMATION_PLATFORM_FLOW",
    "MARKETING_SMS",
]


class MarketingStream(HubspotStream):
    """Marketing streams base class."""

    @property
    @t.override
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/marketing/v3"


class CampaignStream(MarketingStream):
    """https://developers.hubspot.com/docs/reference/api/marketing/campaigns."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    hs_properties = hubspot properties to pull
    """
    name: str = "campaigns"
    path: str = "/campaigns"
    primary_keys: tuple[str] = ("id",)
    records_jsonpath: str = "$[results][*]"
    schema: dict[str, str] = PropertiesList(
        Property("id", StringType),
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property(
            "properties",
            ObjectType(
                Property("hs_start_date", DateType),
                Property("hs_end_date", DateType),
                Property("hs_color_hex", StringType),
                Property("hs_notes", StringType),
                Property("hs_audience", StringType),
                Property("hs_goal", StringType),
                Property("hs_owner", StringType),
                Property("hs_currency_code", StringType),
                Property("hs_created_by_user_id", StringType),
                Property("hs_campaign_status", StringType),
                Property("hs_object_id", StringType),
                Property("hs_name", StringType),
                Property("hs_budget_items_sum_amount", StringType),
                Property("hs_spend_items_sum_amount", StringType),
            ),
        ),
    ).to_dict()

    hs_properties: t.ClassVar = [
        "hs_start_date",
        "hs_end_date",
        "hs_color_hex",
        "hs_notes",
        "hs_audience",
        "hs_goal",
        "hs_owner",
        "hs_currency_code",
        "hs_created_by_user_id",
        "hs_campaign_status",
        "hs_object_id",
        "hs_name",
        "hs_budget_items_sum_amount",
        "hs_spend_items_sum_amount",
    ]

    @t.override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params = super().get_url_params(context, next_page_token)
        params["properties"] = ",".join(self.hs_properties)
        return params

    @t.override
    def generate_child_contexts(
        self,
        record: dict[str, str],
        context: Context | None,
    ) -> t.Generator[dict[str, str]]:
        end_date: datetime = datetime.now(UTC)
        start_date: datetime = end_date - relativedelta(years=3)

        for asset in ASSET_TYPES:
            yield {
                "campaignId": record["id"],
                "asset": asset,
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
            }


class CampaignRevenueStream(MarketingStream):
    """Campaign revenue stream."""

    """
    name: stream name
    parent_stream_type: parent stream
    ignore_parent_replication_keys: flag to ignore the parent's replication
    state_partition_keys: list of keys for partitioning
    path: path which will be added to api url in client.py
    schema: instream schema
    """
    name: str = "campaign_revenue"
    parent_stream_type: object = CampaignStream
    ignore_parent_replication_keys: bool = True
    state_partitioning_keys = ["campaignId", "startDate", "endDate"]

    path: str = (
        "/campaigns/{campaignId}/reports/revenue?startDate="
        "{startDate}&endDate={endDate}"
    )
    schema = PropertiesList(
        Property("campaignId", StringType),
        Property("startDate", DateType),
        Property("endDate", DateType),
        Property("currencyCode", StringType),
        Property("revenueAmount", NumberType),
        Property("dealAmount", NumberType),
        Property("contactsNumber", IntegerType),
        Property("dealsNumber", IntegerType),
    ).to_dict()


class CampaignMetricsStream(MarketingStream):
    """Campaign metrics stream."""

    """
    name: stream name
    parent_stream_type: parent stream
    ignore_parent_replication_keys: flag to ignore the parent's replication
    state_partition_keys: list of keys for partitioning
    path: path which will be added to api url in client.py
    schema: instream schema
    """
    name: str = "campaign_metrics"
    parent_stream_type: object = CampaignStream
    ignore_parent_replication_keys: bool = True
    state_partitioning_keys = ["campaignId", "startDate", "endDate"]
    path: str = (
        "/campaigns/{campaignId}/reports/metrics?startDate="
        "{startDate}&endDate={endDate}"
    )
    schema = PropertiesList(
        Property("campaignId", StringType),
        Property("startDate", DateType),
        Property("endDate", DateType),
        Property("sessions", IntegerType),
        Property("newContactsFirstTouch", IntegerType),
        Property("influencedContacts", IntegerType),
        Property("newContactsLastTouch", IntegerType),
    ).to_dict()


class CampaignAssetsStream(MarketingStream):
    """Campaign Assets stream."""

    """
    name: stream name
    parent_stream_type: parent stream
    ignore_parent_replication_keys: flag to ignore the parent's replication
    state_partition_keys: list of keys for partitioning
    path: path which will be added to api url in client.py
    schema: instream schema
    """
    name: str = "campaign_assets"
    parent_stream_type: object = CampaignStream
    ignore_parent_replication_keys: bool = True
    state_partitioning_keys: list[str] = ["campaignId", "startDate", "endDate", "asset"]
    path: str = (
        "/campaigns/{campaignId}/assets/{asset}?startDate={startDate}&endDate={endDate}"
    )
    schema = PropertiesList(
        Property("id", StringType),
        Property("name", StringType),
        Property("campaignId", StringType),
        Property("startDate", DateType),
        Property("endDate", DateType),
        Property(
            "metrics",
            ObjectType(
                Property("CLICKS", NumberType),
                Property("OPEN", NumberType),
                Property("SENT", NumberType),
                Property("CONTACTS_FIRST_TOUCH", NumberType),
                Property("CONTACTS_LAST_TOUCH", NumberType),
                Property("SUBMISSIONS", NumberType),
                Property("VIEWS", NumberType),
                Property("FACEBOOK_CLICKS", NumberType),
                Property("LINKEDIN_CLICKS", NumberType),
                Property("TWITTER_CLICKS", NumberType),
                Property("CONVERSION_RATE", NumberType),
                Property("CUSTOMERS", NumberType),
                Property("ATTENDEES", NumberType),
                Property("CANCELLATIONS", NumberType),
                Property("REGISTRATIONS", NumberType),
                Property("CONTACTS", NumberType),
                Property("CURRENTLY_ENROLLED", NumberType),
                Property("STARTED", NumberType),
                Property("DELIVERED", NumberType),
                Property("UNIQUE_CLICKS", NumberType),
            ),
        ),
    ).to_dict()
