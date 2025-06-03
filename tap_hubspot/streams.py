"""Stream type classes for tap-hubspot."""

from __future__ import annotations

import datetime
import typing as t

import requests
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot.client import (
    DynamicIncrementalHubspotStream,
    HubspotStream,
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
NumberType = th.NumberType


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

    def get_child_context(self, record: dict, context: Context | None) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "contact_id": record["id"],
        }

    def post_process(
        self,
        row: dict,
        context: Context | None = None,
    ) -> dict | None:
        """Override to handle replication key extraction properly for full table replication."""
        # Call parent post_process first
        row = super().post_process(row, context)
        if row is None:
            return None

        # Ensure replication key has a valid value for state management
        if self.replication_key and self.replication_key in row:
            replication_value = row.get(self.replication_key)
            # If replication key is None/null, try to use updatedAt as fallback
            if replication_value is None:
                if props := row.get("properties"):
                    # Try alternative timestamp fields
                    replication_value = (
                        props.get("lastmodifieddate")
                        or props.get("hs_lastmodifieddate")
                        or row.get("updatedAt")
                    )
                    if replication_value:
                        row[self.replication_key] = replication_value
                    else:
                        # If still no replication value found, use createdAt or updatedAt from top level
                        fallback_value = row.get("updatedAt") or row.get("createdAt")
                        if fallback_value:
                            row[self.replication_key] = fallback_value
                        else:
                            # As last resort, skip the record to avoid None replication key
                            return None

        return row


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


class PropertyTicketStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_tickets"
    path = "/properties/tickets"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyDealStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_deals"
    path = "/properties/deals"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
        Property("calculationFormula", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyContactStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_contacts"
    path = "/properties/contacts"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyCompanyStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_companies"
    path = "/properties/company"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyProductStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_products"
    path = "/properties/product"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyLineItemStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_line_items"
    path = "/properties/line_item"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyEmailStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_emails"
    path = "/properties/email"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyPostalMailStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_postal_mails"
    path = "/properties/postal_mail"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyGoalStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "goal_targets"
    path = "/properties/goal_targets"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyCallStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_calls"
    path = "/properties/call"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyMeetingStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_meetings"
    path = "/properties/meeting"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyTaskStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_tasks"
    path = "/properties/task"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyCommunicationStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "property_communications"
    path = "/properties/communication"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"


class PropertyNotesStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "properties"
    path = "/properties/notes"
    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
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
        Property("hubspot_object", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm/v3"

    def get_records(self, context: Context | None) -> t.Iterable[dict[str, t.Any]]:
        """Merges all the property stream data into a single property table."""
        property_ticket = PropertyTicketStream(self._tap, schema={"properties": {}})
        property_deal = PropertyDealStream(self._tap, schema={"properties": {}})
        property_contact = PropertyContactStream(self._tap, schema={"properties": {}})
        property_company = PropertyCompanyStream(self._tap, schema={"properties": {}})
        property_product = PropertyProductStream(self._tap, schema={"properties": {}})
        property_lineitem = PropertyLineItemStream(self._tap, schema={"properties": {}})
        property_email = PropertyEmailStream(self._tap, schema={"properties": {}})
        property_postalmail = PropertyPostalMailStream(
            self._tap,
            schema={"properties": {}},
        )
        property_call = PropertyCallStream(self._tap, schema={"properties": {}})
        property_goal = PropertyGoalStream(self._tap, schema={"properties": {}})
        property_meeting = PropertyMeetingStream(self._tap, schema={"properties": {}})
        property_task = PropertyTaskStream(self._tap, schema={"properties": {}})
        property_communication = PropertyCommunicationStream(
            self._tap,
            schema={"properties": {}},
        )
        return (
            list(property_ticket.get_records(context))
            + list(property_deal.get_records(context))
            + list(property_contact.get_records(context))
            + list(property_company.get_records(context))
            + list(property_product.get_records(context))
            + list(property_lineitem.get_records(context))
            + list(property_email.get_records(context))
            + list(property_postalmail.get_records(context))
            + list(property_call.get_records(context))
            + list(property_goal.get_records(context))
            + list(property_meeting.get_records(context))
            + list(property_task.get_records(context))
            + list(property_communication.get_records(context))
            + list(super().get_records(context))
        )


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


class EmailEventsStream(HubspotStream):
    """HubSpot Email Events Stream.

    Collects marketing email-related events, such as clicks and status changes.
    Uses offset-based pagination and fetches events in batches.
    """

    name = "email_events"
    path = "/email/public/v1/events"
    primary_keys = ("id",)
    replication_key = "created"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[events][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property("emailCampaignId", IntegerType),
        Property("recipient", StringType),
        Property("type", StringType),
        Property("created", IntegerType),  # Keep as IntegerType to match API response
        Property("url", StringType),
        Property("urlId", IntegerType),
        Property("linkId", IntegerType),
        Property("userAgent", StringType),
        Property("ipAddress", StringType),
        Property(
            "browser",
            ObjectType(
                Property("name", StringType),
                Property("family", StringType),
                Property("producer", StringType),
                Property("producerUrl", StringType),
                Property("type", StringType),
                Property("url", StringType),
                Property("version", StringType),
            ),
        ),
        Property(
            "location",
            ObjectType(
                Property("city", StringType),
                Property("state", StringType),
                Property("country", StringType),
                Property("zipcode", StringType),
                Property("latitude", NumberType),
                Property("longitude", NumberType),
            ),
        ),
        Property("referer", StringType),
        Property("portalId", IntegerType),
        Property("appId", IntegerType),
        Property(
            "sentBy",
            ObjectType(
                Property("id", StringType),
                Property("created", IntegerType),  # Also integer in nested object
            ),
        ),
        Property("smtpId", StringType),
        Property("status", StringType),
        Property("response", StringType),
        Property("attempt", IntegerType),
        Property("category", StringType),
        Property("subject", StringType),
        Property("from", StringType),
        Property("cc", ArrayType(StringType)),
        Property("bcc", ArrayType(StringType)),
        # Add commonly seen fields that were missing
        Property("appName", StringType),
        Property("deviceType", StringType),
        Property("filteredEvent", BooleanType),
        Property("duration", IntegerType),
        Property("emailCampaignGroupId", IntegerType),
        Property("source", StringType),
        Property("sourceId", StringType),
        Property(
            "subscriptions",
            ArrayType(
                ObjectType(
                    Property("id", IntegerType),
                    Property("status", StringType),
                    Property(
                        "legalBasisChange",
                        ObjectType(
                            Property("legalBasisType", StringType),
                            Property("legalBasisExplanation", StringType),
                            Property("optState", StringType),
                        ),
                    ),
                )
            ),
        ),
        Property("portalSubscriptionStatus", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns base url for email events."""
        return "https://api.hubapi.com"

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any | None,
    ) -> t.Any | None:
        """Return offset for next page or None if no more pages."""
        resp_json = response.json()
        has_more = resp_json.get("hasMore", False)
        if has_more:
            return resp_json.get("offset")
        return None

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Return URL parameters for email events API."""
        params = {
            "limit": 1000,
        }

        # Add offset for pagination
        if next_page_token:
            params["offset"] = next_page_token

        # Use replication key state for incremental sync
        starting_replication_value = self.get_starting_replication_key_value(context)
        if starting_replication_value:
            # Convert to timestamp if it's an integer (already a timestamp)
            if isinstance(starting_replication_value, int):
                params["startTimestamp"] = starting_replication_value
            else:
                # If it's a datetime string, convert to timestamp
                try:
                    dt = datetime.datetime.fromisoformat(
                        str(starting_replication_value).replace("Z", "+00:00")
                    )
                    params["startTimestamp"] = int(dt.timestamp() * 1000)
                except (ValueError, AttributeError):
                    # Fallback to config start_date if parsing fails
                    if self.config.get("start_date"):
                        start_timestamp = int(
                            datetime.datetime.fromisoformat(
                                self.config["start_date"].replace("Z", "+00:00")
                            ).timestamp()
                            * 1000
                        )
                        params["startTimestamp"] = start_timestamp
        elif self.config.get("start_date"):
            # Only use start_date if no replication state exists (first run)
            start_timestamp = int(
                datetime.datetime.fromisoformat(
                    self.config["start_date"].replace("Z", "+00:00")
                ).timestamp()
                * 1000
            )
            params["startTimestamp"] = start_timestamp

        if self.config.get("end_date"):
            end_timestamp = int(
                datetime.datetime.fromisoformat(
                    self.config["end_date"].replace("Z", "+00:00")
                ).timestamp()
                * 1000
            )
            params["endTimestamp"] = end_timestamp

        return params

    def get_starting_replication_key_value(
        self,
        context: Context | None,
    ) -> t.Any | None:
        """Return the starting replication key value as integer timestamp."""
        # Get the state value
        state_value = super().get_starting_replication_key_value(context)

        # If we have a datetime string from state, convert it to integer timestamp
        if isinstance(state_value, str):
            try:
                dt = datetime.datetime.fromisoformat(state_value.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
            except (ValueError, AttributeError):
                pass

        # If we have an integer, return as-is
        if isinstance(state_value, int):
            return state_value

        # If we have start_date config, convert to integer timestamp
        if self.config.get("start_date"):
            dt = datetime.datetime.fromisoformat(
                self.config["start_date"].replace("Z", "+00:00")
            )
            return int(dt.timestamp() * 1000)

        return state_value

    def compare_replication_key_value(
        self,
        latest_record: dict,
        previous_max: t.Any,
    ) -> bool:
        """Compare replication key values as integers."""
        latest_value = latest_record.get(self.replication_key)

        # Ensure both values are integers for comparison
        if isinstance(latest_value, int) and isinstance(previous_max, int):
            return latest_value >= previous_max

        # Fallback to parent implementation
        return super().compare_replication_key_value(latest_record, previous_max)

    def post_process(
        self,
        row: dict,
        context: Context | None = None,
    ) -> dict | None:
        """Process browser fields to handle arrays and clean up data."""
        # Handle browser object fields that might be arrays
        if "browser" in row and isinstance(row["browser"], dict):
            browser = row["browser"]
            for field in [
                "name",
                "family",
                "producer",
                "producerUrl",
                "type",
                "url",
                "version",
            ]:
                if field in browser:
                    value = browser[field]
                    # If it's an array with one empty string, convert to None
                    if isinstance(value, list):
                        if len(value) == 1 and value[0] == "":
                            browser[field] = None
                        elif len(value) == 1:
                            browser[field] = value[0]
                        elif len(value) == 0:
                            browser[field] = None
                        # If multiple values, keep as string (join them)
                        else:
                            browser[field] = ", ".join(str(v) for v in value if v)

        return row

    def get_child_context(self, record: dict, context: Context | None) -> dict:
        """Return context for child streams."""
        return {
            "event_id": record["id"],
            "event_type": record["type"],
        }


class WebEventsStream(HubspotStream):
    """HubSpot Web Events Stream.

    Collects web activity events associated with contacts.
    Requires contact_id and uses cursor-based pagination.

    NOTE: This implementation only collects web events for contacts that have been
    collected since the last sync, using the replication key state for efficient
    incremental sync with the occurredAfter parameter.
    """

    name = "web_events"
    path = "/events/v3/events"
    primary_keys = ("id",)
    replication_key = "occurredAt"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[results][*]"
    parent_stream_type = ContactStream
    ignore_parent_replication_key = False

    schema = PropertiesList(
        Property("id", StringType),
        Property("objectType", StringType),
        Property("objectId", StringType),
        Property("eventType", StringType),
        Property("occurredAt", DateTimeType),
        Property("utk", StringType),
        Property("sessionId", StringType),
        Property(
            "properties",
            ObjectType(
                Property("hs_base_url", StringType),
                Property("hs_url", StringType),
                Property("hs_referrer", StringType),
                Property("hs_page_title", StringType),
                Property("hs_title", StringType),
                Property("hs_url_domain", StringType),
                Property("hs_url_path", StringType),
                Property("hs_user_agent", StringType),
                Property("hs_session_id", StringType),
                Property("hs_timestamp", StringType),
            ),
        ),
        Property("contact_id", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns base url for web events."""
        return "https://api.hubapi.com"

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any | None,
    ) -> t.Any | None:
        """Return cursor for next page or None if no more pages."""
        resp_json = response.json()
        paging = resp_json.get("paging")
        if paging and paging.get("next"):
            return paging["next"]["after"]
        return None

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Return URL parameters for web events API."""
        params = {
            "objectType": "contact",
            "limit": 10000,  # Increased limit for better performance
        }

        # Log the context for debugging
        if context:
            self.logger.info(f"Web events context: {context}")
        else:
            self.logger.info("Web events: No context provided")

        # Try different approaches for contact filtering
        if context and context.get("contact_id"):
            contact_id = context["contact_id"]
            params["objectId"] = contact_id
            self.logger.info(f"Fetching web events for contact: {contact_id}")
        else:
            # For debugging, let's try without objectId to see if we get any events at all
            self.logger.info("Fetching web events without specific contact filter")
            # Remove the objectId parameter to get all contact events
            # This might help diagnose if the issue is contact-specific

        # Add cursor for pagination
        if next_page_token:
            params["after"] = next_page_token

        # For debugging, let's use a wider date range
        starting_replication_value = self.get_starting_replication_key_value(context)
        if starting_replication_value:
            params["occurredAfter"] = starting_replication_value
            self.logger.info(f"Using replication key: {starting_replication_value}")
        elif self.config.get("start_date"):
            params["occurredAfter"] = self.config["start_date"]
            self.logger.info(f"Using start_date: {self.config['start_date']}")
        else:
            # For debugging, let's try without date filter
            self.logger.info("No date filter applied")

        self.logger.info(f"Web events API params: {params}")
        return params

    def prepare_request(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> requests.PreparedRequest:
        """Prepare the request and log it for debugging."""
        request = super().prepare_request(context, next_page_token)
        self.logger.info(f"Web events API URL: {request.url}")
        return request

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the API response and extract records."""
        try:
            resp_json = response.json()

            # Debug logging - let's see what we get
            self.logger.info(f"Web events API response status: {response.status_code}")
            self.logger.info(
                f"Web events response keys: {list(resp_json.keys()) if resp_json else 'None'}"
            )

            if response.status_code != 200:
                self.logger.error(f"Web events API error: {resp_json}")
                return

            if "results" in resp_json:
                results = resp_json["results"]
                self.logger.info(f"Found {len(results)} web events")
                if len(results) > 0:
                    # Log first event for debugging
                    self.logger.info(f"First web event sample: {results[0]}")
                for record in results:
                    yield record
            else:
                self.logger.warning(
                    f"No 'results' key in web events response. Available keys: {list(resp_json.keys())}"
                )
                # Log the full response for debugging (truncated)
                response_str = str(resp_json)[:1000]
                self.logger.info(f"Full response (truncated): {response_str}")

        except Exception as e:
            self.logger.error(f"Error parsing web events response: {e}")
            self.logger.error(f"Response content: {response.text[:1000]}")
            raise

    def post_process(
        self,
        row: dict,
        context: Context | None = None,
    ) -> dict | None:
        """Add contact_id from context for easier reference."""
        if context and context.get("contact_id"):
            row["contact_id"] = context["contact_id"]
        return row


class FormSubmissionsStream(HubspotStream):
    """HubSpot Form Submissions Stream (child of ContactStream).

    Fetches form submissions for contacts using the v1 batch endpoint.
    """
    name = "form_submissions"
    parent_stream_type = ContactStream
    ignore_parent_replication_key = False
    primary_keys = ("contact_id", "formId", "timestamp")
    records_jsonpath = "$[*]"  # We'll yield a flat list

    schema = PropertiesList(
        Property("contact_id", StringType),
        Property("formId", StringType),
        Property("formType", StringType),
        Property("timestamp", IntegerType),
        Property("pageUrl", StringType),
        Property("pageTitle", StringType),
        Property("portalId", IntegerType),
        Property("conversionId", StringType),
        Property("formInstanceId", StringType),
        Property("formName", StringType),
        Property("formVersion", StringType),
        Property("formUrl", StringType),
        Property("formFields", ArrayType(ObjectType(
            Property("name", StringType),
            Property("value", StringType),
        ))),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com"

    def get_records(self, context: t.Optional[dict]) -> t.Iterable[dict]:
        import logging
        logger = getattr(self, 'logger', logging.getLogger(__name__))
        session = requests.Session()
        session.headers.update(self.http_headers)
        session.auth = self.authenticator
        endpoint = f"{self.url_base}/contacts/v1/contact/vids/batch"

        FIELD_MAP = {
            "form-id": "formId",
            "form-type": "formType",
            "timestamp": "timestamp",
            "page-url": "pageUrl",
            "page-title": "pageTitle",
            "portal-id": "portalId",
            "conversion-id": "conversionId",
            "form-instance-id": "formInstanceId",
            "form-name": "formName",
            "form-version": "formVersion",
            "form-url": "formUrl",
            "meta-data": "formFields",
        }

        # If context is provided, fetch for just that contact
        if context and "contact_id" in context:
            contact_id = context["contact_id"]
            vid_params = f"vid={contact_id}"
            url = f"{endpoint}?property=vid&formSubmissionMode=all&includeAssociations=true&{vid_params}"
            try:
                resp = session.get(url, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                contact_data = data.get(str(contact_id), {})
                form_submissions = contact_data.get("form-submissions", [])
                for form in form_submissions:
                    mapped = {FIELD_MAP.get(k, k): v for k, v in form.items()}
                    mapped["contact_id"] = contact_id
                    yield mapped
            except Exception as e:
                logger.error(f"Failed to fetch form submissions for contact {contact_id}: {e}")
            return

        # If no context, do nothing
        return

    def get_child_context(self, record: dict, context: t.Optional[dict]) -> dict:
        return {"contact_id": record["contact_id"]}

    def post_process(self, row: dict, context: t.Optional[dict] = None) -> dict | None:
        # Optionally, flatten or clean up fields
        return row
