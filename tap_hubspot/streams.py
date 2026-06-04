"""Stream type classes for tap-hubspot."""

from __future__ import annotations

import typing as t
from functools import cached_property

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot.client import (
    DynamicIncrementalHubspotStream,
    HubspotStream,
    PropertyStream,
)

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType


class ContactStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/contacts."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "contacts"
    required_scopes = ("crm.objects.contacts.read",)
    path = "/objects/contacts"
    incremental_path = "/objects/contacts/search"
    primary_keys = ("id",)
    replication_key = "lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class UsersStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/settings/user-provisioning."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = id keys for replication
    records_jsonpath = json response body
    """

    name = "users"
    required_scopes = ("settings.users.read",)
    path = "/users"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("id", StringType),
        Property("email", StringType),
        Property("roleIds", ArrayType(StringType)),
        Property("primaryteamid", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/settings/v3"


class TeamsStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/settings/teams."""

    name = "teams"
    required_scopes = ("settings.users.teams.read",)
    path = "/users/teams"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property("name", StringType),
        Property("userIds", ArrayType(StringType)),
        Property("secondaryUserIds", ArrayType(StringType)),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/settings/v3"


class OwnersStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/owners#endpoint?spec=GET-/crm/v3/owners/."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "owners"
    required_scopes = ("crm.objects.owners.read",)
    path = "/owners"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("id", StringType),
        Property("email", StringType),
        Property("firstName", StringType),
        Property("lastName", StringType),
        Property("userId", IntegerType),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class TicketPipelineStream(HubspotStream):
    """https://legacydocs.hubspot.com/docs/methods/tickets/get-all-tickets."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "ticket_pipelines"
    required_scopes = ("tickets",)
    path = "/pipelines/tickets"
    primary_keys = ("createdAt",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm-pipelines/v1"


class DealPipelineStream(HubspotStream):
    """https://legacydocs.hubspot.com/docs/methods/deals/get-all-deals."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "deal_pipelines"
    required_scopes = ("crm.objects.deals.read",)
    path = "/pipelines/deals"
    primary_keys = ("createdAt",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm-pipelines/v1"


class EmailSubscriptionStream(HubspotStream):
    """https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = id keys for replication
    records_jsonpath = json response body
    """

    name = "email_subscriptions"
    required_scopes = ("communication_preferences.read_write",)
    path = "/subscriptions"
    primary_keys = ("id",)
    records_jsonpath = "$[subscriptionDefinitions][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/email/public/v1"


class PropertyTicketStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_tickets"
    required_scopes = ("crm.schemas.tickets.read",)
    path = "/properties/tickets"


class PropertyDealStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_deals"
    required_scopes = ("crm.schemas.deals.read",)
    path = "/properties/deals"


class PropertyContactStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_contacts"
    required_scopes = ("crm.schemas.contacts.read",)
    path = "/properties/contacts"


class PropertyCompanyStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_companies"
    required_scopes = ("crm.schemas.companies.read",)
    path = "/properties/company"


class PropertyProductStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_products"
    required_scopes = ("crm.schemas.products.read",)
    path = "/properties/product"


class PropertyLineItemStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_line_items"
    required_scopes = ("crm.schemas.line_items.read",)
    path = "/properties/line_item"


class PropertyEmailStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_emails"
    required_scopes = ("crm.schemas.emails.read",)
    path = "/properties/email"


class PropertyPostalMailStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_postal_mails"
    required_scopes = ("crm.schemas.postal_mail.read",)
    path = "/properties/postal_mail"


class PropertyGoalStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "goal_targets"
    required_scopes = ("crm.schemas.goals.read",)
    path = "/properties/goal_targets"


class PropertyCallStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_calls"
    required_scopes = ("crm.schemas.calls.read",)
    path = "/properties/call"


class PropertyMeetingStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_meetings"
    required_scopes = ("crm.schemas.meetings.read",)
    path = "/properties/meeting"


class PropertyTaskStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_tasks"
    required_scopes = ("crm.schemas.tasks.read",)
    path = "/properties/task"


class PropertyCommunicationStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_communications"
    required_scopes = ("crm.schemas.communications.read",)
    path = "/properties/communication"


class PropertyNotesStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "properties"
    required_scopes = ("crm.schemas.contacts.read",)
    path = "/properties/notes"

    def get_records(self, context: Context | None) -> t.Iterable[dict[str, t.Any]]:
        """Merges all the property stream data into a single property table."""
        property_stream_classes: list[type[PropertyStream]] = [
            PropertyTicketStream,
            PropertyDealStream,
            PropertyContactStream,
            PropertyCompanyStream,
            PropertyProductStream,
            PropertyLineItemStream,
            PropertyEmailStream,
            PropertyPostalMailStream,
            PropertyCallStream,
            PropertyGoalStream,
            PropertyMeetingStream,
            PropertyTaskStream,
            PropertyCommunicationStream,
        ]

        for stream_cls in property_stream_classes:
            stream = stream_cls(self._tap)
            yield from stream.get_records(context)

        yield from super().get_records(context)


class CompanyStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/companies.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "companies"
    required_scopes = ("crm.objects.companies.read",)
    path = "/objects/companies"
    incremental_path = "/objects/companies/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class DealStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/deals."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "deals"
    required_scopes = ("crm.objects.deals.read",)
    path = "/objects/deals"
    incremental_path = "/objects/deals/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class LeadStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/leads."""

    name = "leads"
    required_scopes = ("crm.objects.leads.read",)
    path = "/objects/leads"
    incremental_path = "/objects/leads/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class FeedbackSubmissionsStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/feedback-submissions."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "feedback_submissions"
    required_scopes = ("crm.objects.feedback_submissions.read",)
    path = "/objects/feedback_submissions"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class LineItemStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/line-items."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "line_items"
    required_scopes = ("crm.objects.line_items.read",)
    path = "/objects/line_items"
    incremental_path = "/objects/line_items/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class ProductStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/products."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "products"
    required_scopes = ("e-commerce",)
    path = "/objects/products"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class TicketStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/tickets."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "tickets"
    required_scopes = ("crm.objects.tickets.read",)
    path = "/objects/tickets"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class QuoteStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/quotes.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "quotes"
    required_scopes = ("crm.objects.quotes.read",)
    path = "/objects/quotes"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

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
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class GoalStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/goals.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "goal_targets"
    required_scopes = ("crm.objects.goals.read",)
    path = "/objects/goal_targets"
    incremental_path = "/objects/goal_targets/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class CallStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/calls.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "calls"
    required_scopes = ("crm.objects.calls.read",)
    path = "/objects/calls"
    incremental_path = "/objects/calls/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class CommunicationStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/communications.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "communications"
    required_scopes = ("crm.objects.communications.read",)
    path = "/objects/communications"
    incremental_path = "/objects/communications/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class EmailStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/email."""

    name = "emails"
    required_scopes = ("sales-email-read",)
    path = "/objects/emails"
    incremental_path = "/objects/emails/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class MeetingStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/meetings.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "meetings"
    required_scopes = ("crm.objects.meetings.read",)
    path = "/objects/meetings"
    incremental_path = "/objects/meetings/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class NoteStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/notes.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "notes"
    required_scopes = ("crm.objects.notes.read",)
    path = "/objects/notes"
    incremental_path = "/objects/notes/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PostalMailStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/postal-mail.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "postal_mail"
    required_scopes = ("crm.objects.postal_mail.read",)
    path = "/objects/postal_mail"
    incremental_path = "/objects/postal_mail/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class TaskStream(DynamicIncrementalHubspotStream):
    """https://developers.hubspot.com/docs/api/crm/tasks.

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "tasks"
    required_scopes = ("crm.objects.tasks.read",)
    path = "/objects/tasks"
    incremental_path = "/objects/tasks/search"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class CustomObjectSchemaStream(HubspotStream):
    """Internal helper: discovers properties for a single custom CRM object type.

    Not registered as a tap stream — used only by CustomObjectStream.hs_properties.
    """

    primary_keys = ("name",)
    records_jsonpath = "$.properties[*]"

    @property
    def url_base(self) -> str:  # noqa: D102
        return "https://api.hubapi.com/crm-object-schemas/v3"

    @property
    def path(self) -> str:  # type: ignore[override]  # noqa: D102
        return f"/schemas/{self.name}"


class CustomObjectStream(DynamicIncrementalHubspotStream):
    """Incremental stream for a HubSpot custom CRM object.

    One instance is created per entry in the `custom_object_types` config list.
    Schema is discovered dynamically from the HubSpot schema API at sync time.
    Falls back to full-table refresh when hs_lastmodifieddate is absent from
    the object's schema.
    """

    required_scopes = ("crm.objects.custom.read", "crm.schemas.custom.read")
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"

    def __init__(self, tap: t.Any, object_type: str) -> None:  # noqa: D107
        self._object_type = object_type
        super().__init__(tap, name=object_type)
        # Set as instance attributes so prepare_request can reassign self.path
        # when switching to the incremental search endpoint
        self.path = f"/objects/{object_type}"
        self.incremental_path = f"/objects/{object_type}/search"

    @property
    def url_base(self) -> str:  # noqa: D102
        return "https://api.hubapi.com/crm/v3"

    @cached_property
    def hs_properties(self) -> dict[str, str]:  # noqa: D102
        schema_stream = CustomObjectSchemaStream(self._tap, self._object_type)
        return {prop["name"]: prop["type"] for prop in schema_stream.get_records(None)}

    def _is_incremental_search(self, context: t.Any) -> bool:
        return (
            "hs_lastmodifieddate" in self.hs_properties
            and super()._is_incremental_search(context)
        )

    def post_process(  # noqa: D102
        self,
        row: dict,
        context: t.Any = None,  # noqa: ARG002
    ) -> dict | None:
        if self.replication_key:
            props = row.get("properties") or {}
            row[self.replication_key] = props.get(self.replication_key)
        return row
