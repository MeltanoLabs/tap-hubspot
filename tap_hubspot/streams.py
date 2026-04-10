"""Stream type classes for tap-hubspot."""

from __future__ import annotations

import datetime
import typing as t
from collections.abc import Mapping

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot.client import (
    DynamicIncrementalHubspotStream,
    HubspotStream,
    PropertyStream,
)

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType

HUBSPOT_SEARCH_PAGE_LIMIT = 100
HUBSPOT_SEARCH_RESULT_LIMIT = 10000


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


class PropertyTicketStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_tickets"
    path = "/properties/tickets"


class PropertyDealStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_deals"
    path = "/properties/deals"


class PropertyContactStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_contacts"
    path = "/properties/contacts"


class PropertyCompanyStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_companies"
    path = "/properties/company"


class PropertyProductStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_products"
    path = "/properties/product"


class PropertyLineItemStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_line_items"
    path = "/properties/line_item"


class PropertyEmailStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_emails"
    path = "/properties/email"


class PropertyPostalMailStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_postal_mails"
    path = "/properties/postal_mail"


class PropertyGoalStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "goal_targets"
    path = "/properties/goal_targets"


class PropertyCallStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_calls"
    path = "/properties/call"


class PropertyMeetingStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_meetings"
    path = "/properties/meeting"


class PropertyTaskStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_tasks"
    path = "/properties/task"


class PropertyCommunicationStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "property_communications"
    path = "/properties/communication"


class PropertyNotesStream(PropertyStream):
    """https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}."""

    """
    name: stream name
    path: path which will be added to api url in client.py
    """

    name = "properties"
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


class CustomObjectSchemasStream(HubspotStream):
    """https://developers.hubspot.com/docs/api/crm-object-schemas.

    Streams CRM custom object schemas from the `crm-object-schemas` API.
    """

    name = "custom_object_schemas"
    path = "/schemas"
    primary_keys = ("id",)
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property("name", StringType),
        Property("objectTypeId", StringType),
        Property("objectType", StringType),
        Property(
            "labels",
            ObjectType(
                Property("singular", StringType),
                Property("plural", StringType),
            ),
        ),
        Property("archived", BooleanType),
        Property(
            "properties",
            ArrayType(
                ObjectType(
                    Property("name", StringType),
                    Property("label", StringType),
                    Property("type", StringType),
                ),
            ),
        ),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Returns an updated path which includes the api version."""
        return "https://api.hubapi.com/crm-object-schemas/v3"

    def generate_child_contexts(
        self,
        record: dict[str, object],
        context: Context | None,  # noqa: ARG002
    ) -> t.Iterator[dict[str, object]]:
        """Yield child contexts for `CustomObjectsStream`.

        The child needs the `objectTypeId` (or the API `name`) to target
        the `/crm/objects/{objectType}` endpoint.
        """
        api_name = record.get("name")
        object_type_id = record.get("objectTypeId")
        if not api_name and not object_type_id:
            return
        yield {
            "object_type_id": object_type_id,
            "object_api_name": api_name,
            "properties": record.get("properties", []),
        }


class CustomObjectsStream(DynamicIncrementalHubspotStream):
    """Combined stream that yields records for all custom objects.

    This stream discovers custom object schemas via
    `CustomObjectSchemasStream` and, for each schema, instantiates
    `CustomObjectRecordStream` to fetch records and yield them.
    """

    name = "custom_objects"
    primary_keys = ("id",)
    replication_key = "hs_lastmodifieddate"
    replication_method = "INCREMENTAL"
    state_partitioning_keys: t.ClassVar[list[str]] = ["object_type_id"]
    records_jsonpath = "$[results][*]"

    schema = PropertiesList(
        Property("id", StringType),
        Property("objectTypeId", StringType),
        Property("name", StringType),
        Property(
            "properties",
            ObjectType(additional_properties=StringType(nullable=True)),
        ),
        Property("createdAt", DateTimeType),
        Property("updatedAt", DateTimeType),
        Property("hs_lastmodifieddate", DateTimeType),
        Property("archived", BooleanType),
    ).to_dict()

    parent_stream_type = CustomObjectSchemasStream

    @property
    def url_base(self) -> str:  # noqa: D102
        return "https://api.hubapi.com"

    @staticmethod
    def _get_context_object_type(context: Context | None) -> str | None:
        """Return the HubSpot object type from a child stream context."""
        if not context:
            return None

        object_type = context.get("object_type_id") or context.get(
            "object_api_name",
        )
        return object_type if isinstance(object_type, str) else None

    def _get_property_names(self, context: Context | None) -> list[str]:
        """Return HubSpot property names from a child stream context."""
        property_names: list[str] = []
        if context:
            properties = context.get("properties", [])
            if isinstance(properties, list):
                for prop in properties:
                    if not isinstance(prop, Mapping):
                        continue

                    name = t.cast("Mapping[str, object]", prop).get("name")
                    if isinstance(name, str):
                        property_names.append(name)

        if self.replication_key and self.replication_key not in property_names:
            property_names.append(self.replication_key)

        return property_names

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict[str, int | str]:
        """Return params without dynamic property discovery."""
        if self._is_incremental_search(context):
            return {}

        params: dict[str, int | str] = {}
        if next_page_token:
            params["after"] = next_page_token

        property_names = self._get_property_names(context)
        if property_names:
            params["properties"] = ",".join(property_names)

        return params

    def prepare_request(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> requests.PreparedRequest:
        """Use GET for list requests and POST for incremental search requests."""
        if self._is_incremental_search(context):
            self.path = t.cast("str", self.incremental_path)
            self.http_method = "POST"
        else:
            object_type = self._get_context_object_type(context)
            if object_type:
                self.path = f"/crm/v3/objects/{object_type}"
            self.http_method = "GET"

        return HubspotStream.prepare_request(self, context, next_page_token)

    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict[str, object] | None:
        """Prepare HubSpot Search payload for incremental custom object syncs."""
        if not self._is_incremental_search(context):
            return None

        body: dict[str, object] = {}
        if next_page_token:
            if int(next_page_token) + HUBSPOT_SEARCH_PAGE_LIMIT >= (
                HUBSPOT_SEARCH_RESULT_LIMIT
            ):
                state = self.get_context_state(context)
                self.finalize_state_progress_markers(state)
            else:
                body["after"] = next_page_token

        replication_key_value = t.cast("str", self.replication_key_value)
        ts = datetime.datetime.fromisoformat(replication_key_value)
        epoch_ts = str(int(ts.timestamp() * 1000))

        body.update(
            {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": self.replication_key,
                                "operator": "GTE",
                                "value": epoch_ts,
                            },
                        ],
                    },
                ],
                "sorts": [
                    {
                        "propertyName": self.replication_key,
                        "direction": "ASCENDING",
                    },
                ],
                "limit": HUBSPOT_SEARCH_PAGE_LIMIT,
                "properties": self._get_property_names(context),
            },
        )

        return body

    def post_process(
        self,
        row: dict[str, object],
        context: Context | None = None,
    ) -> dict[str, object] | None:
        """Attach parent custom object metadata to each record."""
        props = row.get("properties")
        if isinstance(props, Mapping):
            row["hs_lastmodifieddate"] = t.cast(
                "Mapping[str, object]",
                props,
            ).get("hs_lastmodifieddate")
        if context:
            row["objectTypeId"] = context.get("object_type_id")

        return row

    # The path must exist before the SDK performs metrics/request setup.
    # Set the per-object path from the parent-provided context at the
    # start of `get_records` so `self.path` is available to the SDK.

    def get_records(
        self,
        context: Context | None,
    ) -> t.Iterable[dict[str, object]]:
        """Return records for one parent custom object context."""
        # Expect the parent `CustomObjectSchemasStream` to call this stream
        # with a context containing `object_type_id` or `object_api_name`.
        if not context:
            self.logger.warning(
                "No parent context provided to customobjects stream; skipping",
            )
            return []

        object_type = self._get_context_object_type(context)
        if not object_type:
            self.logger.warning(
                "Parent context missing object type information; skipping",
            )
            return []

        # Set the path before any SDK request/metrics use `self.path`.
        self.path = f"/crm/v3/objects/{object_type}"
        self.incremental_path = f"/crm/v3/objects/{object_type}/search"

        # Delegate to the base class to handle pagination/requests.
        yield from super().get_records(context)


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
