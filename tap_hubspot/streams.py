"""Stream type classes for tap-hubspot."""

from __future__ import annotations

from typing import Any, ClassVar, Iterable, Type

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot.client import (
    DynamicIncrementalHubspotStream,
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

BASE_URL = "https://api.hubapi.com"
CRM_URL_V3 = BASE_URL + "/crm/v3"
SETTINGS_URL_V3 = BASE_URL + "/settings/v3"
MARKETING_v3 = BASE_URL + "/marketing/v3"


class ContactStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/contacts"""

    name = "contacts"
    path = "/objects/contacts"
    incremental_path = "/objects/contacts/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class UsersStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/settings/user-provisioning"""

    name = "users"
    path = "/users"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property("email", StringType),
        Property("roleIds", ArrayType(StringType)),
        Property("primaryteamid", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return SETTINGS_URL_V3


class OwnersStream(HubspotStream):
    name = "owners"
    path = "/owners"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

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

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class TicketPipelineStream(HubspotStream):
    name = "ticket_pipelines"
    path = "/pipelines/tickets"
    primary_keys: ClassVar[list[str]] = ["pipelineId"]
    records_jsonpath = "$[results][*]"

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

    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com/crm-pipelines/v1"


class DealPipelineStream(HubspotStream):
    name = "deal_pipelines"
    path = "/pipelines/deals"
    primary_keys: ClassVar[list[str]] = ["pipelineId"]
    records_jsonpath = "$[results][*]"

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

    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com/crm-pipelines/v1"


class EmailSubscriptionStream(HubspotStream):
    name = "email_subscriptions"
    path = "/subscriptions"
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

    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com/email/public/v1"


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
        path = "/properties/{object_name}"
        primary_keys: ClassVar[list[str]] = ["label"]
        records_jsonpath = "$[results][*]"

        schema = PROPERTY_SCHEMA

        @property
        def url_base(self) -> str:
            return CRM_URL_V3

    return GenericPropertyStream


class PropertyNotesStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}"""

    name = "properties"
    path = "/properties/notes"
    primary_keys: ClassVar[list[str]] = ["name", "referencedObjectType"]
    records_jsonpath = "$[results][*]"

    schema = PROPERTY_SCHEMA

    @property
    def url_base(self) -> str:
        return CRM_URL_V3

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
        ]:
            property_stream = _property_stream(property_type)(
                self._tap, schema={"properties": {}}
            )
            yield from property_stream.get_records(context)


class CompanyStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/companies"""

    name = "companies"
    path = "/objects/companies"
    incremental_path = "/objects/companies/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class DealStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/deals"""

    name = "deals"
    path = "/objects/deals"
    incremental_path = "/objects/deals/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class FeedbackSubmissionsStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/feedback-submissions"""

    name = "feedback_submissions"
    path = "/objects/feedback_submissions"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

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

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class LineItemStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/line-items"""

    name = "line_items"
    path = "/objects/line_items"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_product_id", StringType),
                Property("hs_recurring_billing_period", StringType),
                Property("name", StringType),
                Property("price", StringType),
                Property("quantity", StringType),
                Property("recurringbillingfrequency", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class ProductStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/products"""

    name = "products"
    path = "/objects/products"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("description", StringType),
                Property("hs_cost_of_goods_sold", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_recurring_billing_period", StringType),
                Property("hs_sku", StringType),
                Property("name", StringType),
                Property("price", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class TicketStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/tickets"""

    name = "tickets"
    path = "/objects/tickets"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_pipeline", StringType),
                Property("hs_pipeline_stage", StringType),
                Property("hs_ticket_priority", StringType),
                Property("hubspot_owner_id", StringType),
                Property("subject", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class QuoteStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/quotes"""

    name = "quotes"
    path = "/objects/quotes"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("hs_createdate", StringType),
                Property("hs_expiration_date", StringType),
                Property("hs_quote_amount", StringType),
                Property("hs_quote_number", StringType),
                Property("hs_status", StringType),
                Property("hs_terms", StringType),
                Property("hs_title", StringType),
                Property("hubspot_owner_id", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class GoalStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/goals"""

    name = "goals"
    path = "/objects/goal_targets"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_created_by_user_id", StringType),
                Property("hs_end_datetime", StringType),
                Property("hs_goal_name", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_start_datetime", StringType),
                Property("hs_target_amount", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class CallStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/calls"""

    name = "calls"
    path = "/objects/calls"
    incremental_path = "/objects/calls/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class CommunicationStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/communications"""

    name = "communications"
    path = "/objects/communications"
    incremental_path = "/objects/communications/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class EmailStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/email"""

    name = "emails"
    path = "/objects/emails"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_email_direction", StringType),
                Property("hs_email_sender_email", StringType),
                Property("hs_email_sender_firstname", StringType),
                Property("hs_email_sender_lastname", StringType),
                Property("hs_email_status", StringType),
                Property("hs_email_subject", StringType),
                Property("hs_email_text", StringType),
                Property("hs_email_to_email", StringType),
                Property("hs_email_to_firstname", StringType),
                Property("hs_email_to_lastname", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_timestamp", StringType),
                Property("hubspot_owner_id", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class MeetingStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/meetings"""

    name = "meetings"
    path = "/objects/meetings"
    incremental_path = "/objects/meetings/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class NoteStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/notes"""

    name = "notes"
    path = "/objects/notes"
    incremental_path = "/objects/notes/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class PostalMailStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/postal-mail"""

    name = "postal_mail"
    path = "/objects/postal_mail"
    incremental_path = "/objects/postal_mail/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class TaskStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/tasks"""

    name = "tasks"
    path = "/objects/tasks"
    incremental_path = "/objects/tasks/search"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        return CRM_URL_V3


class FormStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/forms"""

    name = "forms"
    path = "/forms"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property("name", StringType),
        Property("formType", StringType),
        Property("createdAt", DateTimeType),
        Property("updatedAt", DateTimeType),
        Property("archived", BooleanType),
        Property("archivedAt", DateTimeType),
        Property("fieldGroups", th.ArrayType(th.ObjectType())),
        Property("configuration", th.ObjectType()),
        Property("displayOptions", th.ObjectType()),
        Property("legalConsentOptions", th.ObjectType()),
    ).to_dict()

    @property
    def base_url(self) -> str:
        return MARKETING_v3
