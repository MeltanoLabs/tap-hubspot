"""Stream type classes for tap-hubspot."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, ClassVar, Iterable, Type

from singer_sdk import metrics
from singer_sdk import typing as th

from tap_hubspot.client import (
    DynamicHubspotStream,
    DynamicIncrementalHubspotStream,
    HubspotAnalyticsStream,
    HubspotStream,
)

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType
FloatType = th.NumberType

CRM_URL_V3 = "/crm/v3"
SETTINGS_URL_V3 = "/settings/v3"
MARKETING_v3 = "/marketing/v3"
PIPELINES_V1 = "/crm-pipelines/v1/pipelines"


class ContactStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/contacts"""

    name = "contacts"
    path = f"{CRM_URL_V3}/objects/contacts"
    incremental_path = f"{CRM_URL_V3}/objects/contacts/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "lastmodifieddate"
    replication_method = "INCREMENTAL"


class UsersStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/settings/user-provisioning"""

    name = "users"
    path = f"{SETTINGS_URL_V3}/users"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", StringType),
        Property("email", StringType),
        Property("roleIds", ArrayType(StringType)),
        Property("primaryTeamId", StringType),
        Property("secondaryTeamIds", ArrayType(StringType)),
        Property("superAdmin", BooleanType),
    ).to_dict()


class OwnersStream(HubspotStream):
    name = "owners"
    path = f"{CRM_URL_V3}/owners"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", StringType),
        Property("email", StringType),
        Property("firstName", StringType),
        Property("lastName", StringType),
        Property("userId", IntegerType),
        Property("createdAt", DateTimeType),
        Property("updatedAt", DateTimeType),
        Property("archived", BooleanType),
    ).to_dict()


class TicketPipelineStream(HubspotStream):
    name = "ticket_pipelines"
    path = f"{PIPELINES_V1}/tickets"
    primary_keys: ClassVar[list[str]] = ["pipelineId"]

    schema = PropertiesList(
        Property("label", StringType),
        Property("displayOrder", IntegerType),
        Property("active", BooleanType),
        Property(
            "stages",
            ArrayType(
                ObjectType(
                    Property("label", StringType),
                    Property("displayOrder", IntegerType),
                    Property(
                        "metadata",
                        ObjectType(
                            Property("ticketState", StringType),
                            Property("isClosed", StringType),
                        ),
                    ),
                    Property("stageId", StringType),
                    Property("createdAt", IntegerType),
                    Property("updatedAt", IntegerType),
                    Property("active", BooleanType),
                ),
            ),
        ),
        Property("objectType", StringType),
        Property("objectTypeId", StringType),
        Property("pipelineId", StringType),
        Property("createdAt", IntegerType),
        Property("updatedAt", IntegerType),
        Property("default", BooleanType),
    ).to_dict()


class DealPipelineStream(HubspotStream):
    name = "deal_pipelines"
    path = f"{PIPELINES_V1}/deals"
    primary_keys: ClassVar[list[str]] = ["pipelineId"]

    schema = PropertiesList(
        Property("label", StringType),
        Property("displayOrder", IntegerType),
        Property("active", BooleanType),
        Property(
            "stages",
            ArrayType(
                ObjectType(
                    Property("label", StringType),
                    Property("displayOrder", IntegerType),
                    Property(
                        "metadata",
                        ObjectType(
                            Property("isClosed", BooleanType),
                            Property("probability", StringType),
                        ),
                    ),
                    Property("stageId", StringType),
                    Property("createdAt", IntegerType),
                    Property("updatedAt", IntegerType),
                    Property("active", BooleanType),
                ),
            ),
        ),
        Property("objectType", StringType),
        Property("objectTypeId", StringType),
        Property("pipelineId", StringType),
        Property("createdAt", IntegerType),
        Property("updatedAt", IntegerType),
        Property("default", BooleanType),
    ).to_dict()


class EmailSubscriptionStream(HubspotStream):
    name = "email_subscriptions"
    path = "/email/public/v1/subscriptions"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[subscriptionDefinitions][*]"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("portalId", IntegerType),
        Property("name", StringType),
        Property("description", StringType),
        Property("active", BooleanType),
        Property("internal", BooleanType),
        Property("category", StringType),
        Property("channel", StringType),
        Property("internalName", StringType),
        Property("businessUnitId", IntegerType),
    ).to_dict()


PROPERTY_SCHEMA = PropertiesList(
    Property("updatedAt", DateTimeType),
    Property("createdAt", DateTimeType),
    Property("name", StringType),
    Property("label", StringType),
    Property("type", StringType),
    Property("fieldType", StringType),
    Property("description", StringType),
    Property("groupName", StringType),
    Property(
        "options",
        ArrayType(
            ObjectType(
                Property("label", StringType),
                Property("description", StringType),
                Property("value", StringType),
                Property("displayOrder", IntegerType),
                Property("hidden", BooleanType),
            ),
        ),
    ),
    Property("displayOrder", IntegerType),
    Property("calculated", BooleanType),
    Property("externalOptions", BooleanType),
    Property("hasUniqueValue", BooleanType),
    Property("hidden", BooleanType),
    Property("hubspotDefined", BooleanType),
    Property(
        "modificationMetadata",
        ObjectType(
            Property("readOnlyOptions", BooleanType),
            Property("readOnlyValue", BooleanType),
            Property("readOnlyDefinition", BooleanType),
            Property("archivable", BooleanType),
        ),
    ),
    Property("formField", BooleanType),
    Property("referencedObjectType", StringType),
).to_dict()


def _property_stream(object_name: str) -> Type[HubspotStream]:
    class GenericPropertyStream(HubspotStream):
        name = f"property_{object_name}"
        path = f"{CRM_URL_V3}/properties/{object_name}"
        primary_keys: ClassVar[list[str]] = ["label"]

        schema = PROPERTY_SCHEMA

    return GenericPropertyStream


class PropertyStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}"""

    name = "properties"
    path = "/properties"
    primary_keys: ClassVar[list[str]] = ["name", "referencedObjectType"]

    schema = PROPERTY_SCHEMA

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Merges all the property stream data into a single property table"""
        for property_type in [
            "ticket",
            "deal",
            "contact",
            "company",
            "product",
            "line_item",
            "email",
            "postal_mail",
            "call",
            "meeting",
            "task",
            "communication",
            "note",
            "user",
            "goal_targets",
            "feedback_submissions",
            "line_items",
            "products",
            "quotes",
        ]:
            property_stream = _property_stream(property_type)(
                self._tap, schema={"properties": {}}
            )
            for record in property_stream.get_records(context):
                # this should be in post_process, but there is no info on the object type
                yield record | {"referencedObjectType": property_type}


class CompanyStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/companies"""

    name = "companies"
    path = f"{CRM_URL_V3}/objects/companies"
    incremental_path = f"{CRM_URL_V3}/objects/companies/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class DealStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/deals"""

    name = "deals"
    path = f"{CRM_URL_V3}/objects/deals"
    incremental_path = f"{CRM_URL_V3}/objects/deals/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class FeedbackSubmissionsStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/feedback-submissions"""

    name = "feedback_submissions"
    path = f"{CRM_URL_V3}/objects/feedback_submissions"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("city", StringType),
                Property("createdDate", StringType),
                Property("domain", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("industry", StringType),
                Property("name", StringType),
                Property("phone", StringType),
                Property("state", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()


class LineItemStream(DynamicHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/line-items"""

    name = "line_items"
    path = f"{CRM_URL_V3}/objects/line_items"
    primary_keys: ClassVar[list[str]] = ["id"]


class ProductStream(DynamicHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/products"""

    name = "products"
    path = f"{CRM_URL_V3}/objects/products"
    primary_keys: ClassVar[list[str]] = ["id"]


class TicketStream(DynamicHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/tickets"""

    name = "tickets"
    path = f"{CRM_URL_V3}/objects/tickets"
    primary_keys: ClassVar[list[str]] = ["id"]


class QuoteStream(DynamicHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/quotes"""

    name = "quotes"
    path = f"{CRM_URL_V3}/objects/quotes"
    primary_keys: ClassVar[list[str]] = ["id"]


class GoalStream(DynamicHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/goals"""

    name = "goals"
    path = f"{CRM_URL_V3}/objects/goal_targets"
    primary_keys: ClassVar[list[str]] = ["id"]


class CallStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/calls"""

    name = "calls"
    path = f"{CRM_URL_V3}/objects/calls"
    incremental_path = f"{CRM_URL_V3}/objects/calls/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class CommunicationStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/communications"""

    name = "communications"
    path = f"{CRM_URL_V3}/objects/communications"
    incremental_path = f"{CRM_URL_V3}/objects/communications/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class EmailStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/email"""

    name = "emails"
    path = f"{CRM_URL_V3}/objects/emails"
    incremental_path = f"{CRM_URL_V3}/objects/emails/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class MeetingStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/meetings"""

    name = "meetings"
    path = f"{CRM_URL_V3}/objects/meetings"
    incremental_path = f"{CRM_URL_V3}/objects/meetings/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class NoteStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/notes"""

    name = "notes"
    path = f"{CRM_URL_V3}/objects/notes"
    incremental_path = f"{CRM_URL_V3}/objects/notes/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class PostalMailStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/postal-mail"""

    name = "postal_mail"
    path = f"{CRM_URL_V3}/objects/postal_mail"
    incremental_path = f"{CRM_URL_V3}/objects/postal_mail/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class TaskStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/tasks"""

    name = "tasks"
    path = f"{CRM_URL_V3}/objects/tasks"
    incremental_path = f"{CRM_URL_V3}/objects/tasks/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"


class FormStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/forms"""

    name = "forms"
    path = f"{MARKETING_v3}/forms"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = th.PropertiesList(
        Property("id", StringType),
        Property("name", StringType),
        Property("formType", StringType),
        Property("createdAt", DateTimeType),
        Property("updatedAt", DateTimeType),
        Property("archived", BooleanType),
        Property(
            "fieldGroups",
            ArrayType(
                ObjectType(
                    Property("groupType", StringType),
                    Property("richTextType", StringType),
                    Property(
                        "fields",
                        ArrayType(
                            ObjectType(
                                Property("objectTypeId", StringType),
                                Property("name", StringType),
                                Property("label", StringType),
                                Property("required", BooleanType),
                                Property("hidden", BooleanType),
                                Property("fieldType", StringType),
                                Property(
                                    "validation",
                                    ObjectType(
                                        Property(
                                            "blockedEmailDomains", ArrayType(StringType)
                                        ),
                                        Property("useDefaultBlockList", BooleanType),
                                    ),
                                ),
                            )
                        ),
                    ),
                )
            ),
        ),
        Property(
            "configuration",
            ObjectType(
                Property("language", StringType),
                Property("cloneable", BooleanType),
                Property("editable", BooleanType),
                Property("archivable", BooleanType),
                Property("recaptchaEnabled", BooleanType),
                Property("notifyContactOwner", BooleanType),
                Property("notifyRecipients", ArrayType(StringType)),
                Property("createNewContactForNewEmail", BooleanType),
                Property("prePopulateKnownValues", BooleanType),
                Property("allowLinkToResetKnownValues", BooleanType),
                Property(
                    "lifecycleStages",
                    ArrayType(
                        ObjectType(
                            Property("objectTypeId", StringType),
                            Property("value", StringType),
                        )
                    ),
                ),
            ),
        ),
        Property(
            "displayOptions",
            ObjectType(
                Property("renderRawHtml", BooleanType),
                Property("theme", StringType),
                Property("submitButtonText", StringType),
                Property(
                    "style",
                    ObjectType(
                        Property("fontFamily", StringType),
                        Property("backgroundWidth", StringType),
                        Property("labelTextColor", StringType),
                        Property("labelTextSize", StringType),
                        Property("helpTextColor", StringType),
                        Property("helpTextSize", StringType),
                        Property("legalConsentTextColor", StringType),
                        Property("legalConsentTextSize", StringType),
                        Property("submitColor", StringType),
                        Property("submitAlignment", StringType),
                        Property("submitFontColor", StringType),
                        Property("submitSize", StringType),
                    ),
                ),
                Property("cssClass", StringType),
            ),
        ),
        Property(
            "legalConsentOptions",
            ObjectType(
                Property("type", StringType),
                Property("communicationConsentText", StringType),
                Property(
                    "communicationsCheckboxes",
                    ArrayType(
                        ObjectType(
                            Property("required", BooleanType),
                            Property("subscriptionTypeId", IntegerType),
                            Property("label", StringType),
                        )
                    ),
                ),
                Property("consentToProcessText", StringType),
                Property("consentToProcessCheckboxLabel", StringType),
                Property("privacyText", StringType),
            ),
        ),
    ).to_dict()

    def get_child_context(self, record: dict, context: dict | None) -> dict | None:
        return {
            "form_id": record["id"],
        }


class FormSubmissionStream(HubspotStream):
    """https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form"""

    name = "form_submissions"
    path = "/form-integrations/v1/submissions/forms/{form_id}"
    primary_keys: ClassVar[list[str]] = ["form_id", "conversionId"]
    replication_key = "submittedAt"
    ignore_parent_replication_keys = True
    parent_stream_type = FormStream
    limit = 50

    schema = PropertiesList(
        Property("form_id", StringType),
        Property("conversionId", StringType),
        Property("submittedAt", IntegerType),
        Property(
            "values",
            th.ArrayType(
                th.ObjectType(
                    Property("name", StringType),
                    Property("value", StringType),
                )
            ),
        ),
        Property("pageUrl", StringType),
    ).to_dict()

    def request_records(self, context: dict | None) -> Iterable[dict]:
        paginator = self.get_new_paginator()
        decorated_request = self.request_decorator(self._request)
        initial_value = self.get_starting_replication_key_value(context)
        finished = paginator.finished

        with metrics.http_request_counter(self.name, self.path) as request_counter:
            request_counter.context = context

            while not finished:
                prepared_request = self.prepare_request(
                    context,
                    next_page_token=paginator.current_value,
                )
                resp = decorated_request(prepared_request, context)
                request_counter.increment()
                self.update_sync_costs(prepared_request, resp, context)
                # overriding the default pagination logic since this stream returns records in reverse order
                for record in self.parse_response(resp):
                    yield record
                    if initial_value and record["submittedAt"] < convert_date_to_epoch(
                        initial_value
                    ):
                        finished = True
                        break

                if not finished:
                    paginator.advance(resp)
                    finished = paginator.finished


def convert_date_to_epoch(date: str | int) -> int:
    if isinstance(date, str):
        if len(date) == 10:
            dt = datetime.fromisoformat(f"{date}T00:00:00")
        else:
            dt = datetime.fromisoformat(date)
        return (dt - datetime(1970, 1, 1)).total_seconds() * 1000
    return date


class AnalyticsSourcesDaily(HubspotAnalyticsStream):
    name = "analytics_sources_daily"
    path = "/analytics/v2/reports/sources/daily"
    replication_key = "date"
    primary_keys: ClassVar[list[str]] = ["date", "breakdown"]
    schema = th.PropertiesList(
        Property("date", th.DateType),
        Property("breakdown", StringType),
        Property("contactsPerPageview", FloatType),
        Property("returningVisits", IntegerType),
        Property("rawViews", IntegerType),
        Property("standardViews", IntegerType),
        Property("sessionToContactRate", FloatType),
        Property("pageviewsPerSession", FloatType),
        Property("bounceRate", FloatType),
        Property("marketingQualifiedLeads", IntegerType),
        Property("visits", IntegerType),
        Property("visitors", IntegerType),
        Property("pageviewsMinusExits", IntegerType),
        Property("opportunities", IntegerType),
        Property("leads", IntegerType),
        Property("leadsPerView", FloatType),
        Property("bounces", IntegerType),
        Property("time", IntegerType),
        Property("timePerSession", FloatType),
        Property("contacts", IntegerType),
        Property("newVisitorSessionRate", FloatType),
        Property("subscribers", IntegerType),
    ).to_dict()


class AnalyticsSessionsDaily(HubspotAnalyticsStream):
    name = "analytics_sessions_daily"
    path = "/analytics/v2/reports/sessions/daily"
    replication_key = "date"
    primary_keys: ClassVar[list[str]] = ["date", "breakdown"]

    schema = th.PropertiesList(
        Property("date", th.DateType),
        Property("breakdown", StringType),
        Property("others", IntegerType),
        Property("mobile", IntegerType),
        Property("desktop", IntegerType),
        Property("organicSearch", IntegerType),
        Property("emailMarketing", IntegerType),
        Property("paidSearch", IntegerType),
        Property("paidSocial", IntegerType),
        Property("socialMedia", IntegerType),
        Property("directTraffic", IntegerType),
        Property("referrals", IntegerType),
        Property("otherCampaigns", IntegerType),
    ).to_dict()


class AnalyticsPagesTotals(HubspotStream):
    """HubspotAnalyticsPagesTotals"""

    name = "analytics_pages_totals"
    path = "/analytics/v2/reports/pages/total"
    records_jsonpath = "$[breakdowns][*]"
    next_page_token_jsonpath = "$[offset]"
    primary_keys: ClassVar[list[str]] = ["breakdown"]
    replication_key = "last_updated_date"
    limit = 350

    schema = th.PropertiesList(
        Property("meta", StringType),
        Property("last_updated_date", th.DateType),
        Property("breakdown", StringType),
        Property("newVisitorRawViews", IntegerType),
        Property("exits", IntegerType),
        Property("pageviewsMinusExits", IntegerType),
        Property("exitsPerPageview", FloatType),
        Property("rawViews", IntegerType),
        Property("standardViews", IntegerType),
        Property("entrances", IntegerType),
        Property("pageBounceRate", FloatType),
    ).to_dict()

    def get_url_params(
        self, context: dict | None, next_page_token: str | None
    ) -> dict[str, Any]:
        params = {}
        if replication_key_value := self.get_starting_replication_key_value(context):
            # Retrieving last 30 days of data just to be sure
            params["start"] = (
                datetime.strptime(replication_key_value, "%Y-%m-%d")
                - timedelta(days=30)
            ).strftime("%Y-%m-%d")
        if next_page_token:
            params["offset"] = next_page_token
        return params

    def post_process(
        self, row: dict[str, Any], context: dict[str, Any] | None
    ) -> dict[str, Any]:
        row["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
        return row

    def get_child_context(
        self, record: dict[str, Any], context: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        return {"breakdown": record["breakdown"]}


class AnalyticsPagesDaily(HubspotStream):
    name = "analytics_pages_daily"
    primary_keys: ClassVar[list[str]] = ["date", "breakdown"]
    state_partitioning_keys = []
    path = "/analytics/v2/reports/pages/daily"
    parent_stream_type = AnalyticsPagesTotals
    records_jsonpath = "$[*]"

    def get_url_params(
        self, context: dict[str, Any] | None, next_page_token: str | None
    ) -> dict[str, Any]:
        return super().get_url_params(context, next_page_token) | {
            "f": context["breakdown"]
        }

    def get_records(self, context: dict[str, Any] | None) -> Iterable[dict[str, Any]]:
        rows = super().get_records(context)
        for row in rows:
            for date, breakdowns in row.items():
                for breakdown in breakdowns:
                    breakdown["date"] = date
                    yield breakdown

    schema = th.PropertiesList(
        Property("date", th.DateType),
        Property("breakdown", StringType),
        Property("meta", StringType),
        Property("newVisitorRawViews", IntegerType),
        Property("exits", IntegerType),
        Property("pageviewsMinusExits", IntegerType),
        Property("exitsPerPageview", FloatType),
        Property("rawViews", IntegerType),
        Property("pageTime", IntegerType),
        Property("timePerPageview", FloatType),
        Property("entrances", IntegerType),
        Property("pageBounceRate", FloatType),
        Property("standardViews", IntegerType),
    ).to_dict()
