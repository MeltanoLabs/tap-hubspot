"""Stream type classes for tap-hubspot."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot.client import HubspotStream

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType


class ContactStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods/lists/get_lists
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                vid, canonical-vid, merged-vids, portal-id, is-contact, properties
              """

    name = "contact"
    path = "/lists/all/contacts/all?fields={}".format(columns)
    primary_keys = ["addedAt"]
    replication_key = "addedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("vid", IntegerType),
        Property("canonical-vid", IntegerType),
        Property("merged-vids", ArrayType(StringType)),
        Property("portal-id", IntegerType),
        Property("is-contact", BooleanType),
        Property(
            "properties",
            ObjectType(
                Property("lastmodifieddate", StringType),
                Property("email", StringType),
                Property("message", StringType),
                Property("city", StringType),
                Property("company", StringType),
                Property("createddate", StringType),
                Property("firstname", StringType),
                Property("hs_all_contact_vids", IntegerType),
                Property("hs_date_entered_lead", StringType),
                Property("hs_marketable_reason_id", StringType),
                Property("hs_is_unworked", BooleanType),
                Property("hs_marketable_until_renewal", BooleanType),
                Property("hs_latest_source_timestamp", StringType),
                Property("hs_marketable_reason_type", StringType),
                Property("hs_marketable_status", BooleanType),
                Property("hs_is_contact", BooleanType),
                Property("hs_email_domain", StringType),
                Property("hs_pipeline", StringType),
                Property("hs_sequences_actively_enrolled_count", StringType),
                Property("hs_object_id", StringType),
                Property("hs_time_in_lead", StringType),
                Property("num_conversion_events", StringType),
                Property("num_unique_conversion_events", StringType),
                Property("lastname", StringType),
                Property("hs_analytics_num_page_views", StringType),
                Property("hs_analytics_num_event_completions", StringType),
                Property("hs_analytics_first_timestamp", StringType),
                Property("hs_social_twitter_clicks", StringType),
                Property("hs_analytics_num_visits", StringType),
                Property("twitterprofilephoto", StringType),
                Property("twitterhandle", StringType),
                Property("hs_analytics_source_data_2", StringType),
                Property("hs_social_facebook_clicks", StringType),
                Property("hs_analytics_source", StringType),
                Property("hs_analytics_source_data_1", StringType),
                Property("hs_latest_source", StringType),
                Property("hs_latest_source_data_1", StringType),
                Property("hs_latest_source_data_2", StringType),
                Property("hs_social_google_plus_clicks", StringType),
                Property("hs_social_num_broadcast_clicks", StringType),
                Property("state", StringType),
                Property("hs_social_linkedin_clicks", StringType),
                Property("hs_lifecyclestage_lead_date", StringType),
                Property("hs_analytics_revenue", StringType),
                Property("hs_analytics_average_page_views", StringType),
                Property("website", StringType),
                Property("lifecyclestage", StringType),
                Property("jobtitle", StringType),
            ),
        ),
        Property("form-submissions", ArrayType(StringType)),
        Property("identity-profiles", ArrayType(StringType)),
        Property("merge-audits", ArrayType(StringType)),
        Property("addedAt", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/contacts/v1"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        params["property"] = (
            "message",
            "email",
            "city",
            "company",
            "createddate",
            "firstname",
            "hs_all_contact_vids",
            "hs_date_entered_lead",
            "hs_marketable_reason_id",
            "hs_is_unworked",
            "hs_marketable_until_renewal",
            "hs_latest_source_timestamp",
            "hs_marketable_reason_type",
            "hs_marketable_status",
            "hs_is_contact",
            "hs_email_domain",
            "hs_pipeline",
            "hs_sequences_actively_enrolled_count",
            "hs_object_id",
            "hs_time_in_lead",
            "num_conversion_events",
            "num_unique_conversion_events",
            "lastname",
            "hs_analytics_num_page_views",
            "hs_analytics_num_event_completions",
            "hs_analytics_first_timestamp",
            "hs_social_twitter_clicks",
            "hs_analytics_num_visits",
            "twitterprofilephoto",
            "twitterhandle",
            "hs_analytics_source_data_2",
            "hs_social_facebook_clicks",
            "hs_analytics_source",
            "hs_analytics_source_data_1",
            "hs_latest_source",
            "hs_latest_source_data_1",
            "hs_latest_source_data_2",
            "hs_social_google_plus_clicks",
            "hs_social_num_broadcast_clicks",
            "state",
            "hs_social_linkedin_clicks",
            "hs_lifecyclestage_lead_date",
            "hs_analytics_revenue",
            "hs_analytics_average_page_views",
            "website",
            "lifecyclestage",
            "jobtitle",
        )
        params["propertyMode"] = "value_and_history"

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("contacts") is not None:
            results = resp_json["contacts"]
        else:
            results = resp_json

        yield from results


class UsersStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/settings/user-provisioning
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, email, roleIds, primaryteamid
              """

    name = "users"
    path = "/users?fields={}".format(columns)
    primary_keys = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("email", StringType),
        Property("roleIds", ArrayType(StringType)),
        Property("primaryteamid", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/settings/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class OwnersStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/owners#endpoint?spec=GET-/crm/v3/owners/
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, email, firstName, lastName, userId, createdAt, updatedAt, archived
              """

    name = "owners"
    path = "/owners?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class TicketPipelineStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods/tickets/get-all-tickets
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                label, displayOrder, active, stages, objectType, objectTypeId, pipelineId, createdAt, updatedAt, default
              """

    name = "ticketpipeline"
    path = "/pipelines/tickets?fields={}".format(columns)
    primary_keys = ["createdAt"]
    replication_key = "createdAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("label", StringType),
        Property("displayOrder", StringType),
        Property("active", BooleanType),
        Property(
            "stages",
            ArrayType(
                ObjectType(
                    Property("label", StringType),
                    Property("displayOrder", StringType),
                    Property(
                        "metadata",
                        ObjectType(
                            Property("ticketState", StringType),
                            Property("isClosed", StringType),
                        ),
                    ),
                    Property("stageId", IntegerType),
                    Property("createdAt", StringType),
                    Property("updatedAt", StringType),
                    Property("active", StringType),
                ),
            ),
        ),
        Property("objectType", StringType),
        Property("objectTypeId", StringType),
        Property("pipelineId", StringType),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("default", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm-pipelines/v1"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class DealPipelineStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods/deals/get-all-deals
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                label, displayOrder, active, stages, objectType, objectTypeId, pipelineId, createdAt, updatedAt, default
              """

    name = "dealpipeline"
    path = "/pipelines/deals?fields={}".format(columns)
    primary_keys = ["createdAt"]
    replication_key = "createdAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("label", StringType),
        Property("displayOrder", StringType),
        Property("active", BooleanType),
        Property(
            "stages",
            ArrayType(
                ObjectType(
                    Property("label", StringType),
                    Property("displayOrder", StringType),
                    Property(
                        "metadata",
                        ObjectType(
                            Property("isClosed", BooleanType),
                            Property("probability", StringType),
                        ),
                    ),
                    Property("stageId", IntegerType),
                    Property("createdAt", StringType),
                    Property("updatedAt", StringType),
                    Property("active", StringType),
                ),
            ),
        ),
        Property("objectType", StringType),
        Property("objectTypeId", StringType),
        Property("pipelineId", StringType),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("default", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm-pipelines/v1"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class EmailSubscriptionStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, portalId, name, description, active, internal, category, channel, internalName, businessUnitId
              """

    name = "emailsubscription"
    path = "/subscriptions/?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

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
        Property("businessUnitId", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/email/public/v1"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("subscriptionDefinitions") is not None:
            results = resp_json["subscriptionDefinitions"]
        else:
            results = resp_json

        yield from results


class PropertyTicketStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertyticket"
    path = "/properties/tickets?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        row["hubspot_object"] = "ticket"

        return super().post_process(row, context)


class PropertyDealStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertydeal"
    path = "/properties/deals?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("calculationFormula", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "deal"
        except:
            pass

        return super().post_process(row, context)


class PropertyContactStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertycontact"
    path = "/properties/contacts?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "contact"
        except:
            pass

        return super().post_process(row, context)


class PropertyCompanyStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertycompany"
    path = "/properties/company?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "company"
        except:
            pass

        return super().post_process(row, context)


class PropertyProductStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertyproduct"
    path = "/properties/product?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "product"
        except:
            pass

        return super().post_process(row, context)


class PropertyLineItemStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertylineitem"
    path = "/properties/line_item?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "line_item"
        except:
            pass

        return super().post_process(row, context)


class PropertyEmailStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertyemail"
    path = "/properties/email?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "email"
        except:
            pass

        return super().post_process(row, context)


class PropertyPostalMailStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertypostalmail"
    path = "/properties/postal_mail?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "postal_mail"
        except:
            pass

        return super().post_process(row, context)


class PropertyCallStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertycall"
    path = "/properties/call?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "call"
        except:
            pass

        return super().post_process(row, context)


class PropertyMeetingStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertymeeting"
    path = "/properties/meeting?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "meeting"
        except:
            pass

        return super().post_process(row, context)


class PropertyTaskStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertytask"
    path = "/properties/task?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "task"
        except:
            pass

        return super().post_process(row, context)


class PropertyCommunicationStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "propertycommunication"
    path = "/properties/task?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "communication"
        except:
            pass

        return super().post_process(row, context)


class PropertyNotesStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/properties#endpoint?spec=PATCH-/crm/v3/properties/{objectType}/{propertyName}
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                updatedAt, createdAt, name, label, type, fieldType, description, groupName, options, displayOrder,
                calculated, externalOptions, hasUniqueValue, hidden, hubspotDefined, modificationMetadata, formField
              """

    name = "property"
    path = "/properties/notes?fields={}".format(columns)
    replication_key = "updatedAt"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("updatedAt", StringType),
        Property("createdAt", StringType),
        Property("name", StringType),
        Property("label", StringType),
        Property("type", StringType),
        Property("fieldType", StringType),
        Property("description", StringType),
        Property("groupName", StringType),
        Property("options", StringType),
        Property("displayOrder", StringType),
        Property("calculated", BooleanType),
        Property("externalOptions", BooleanType),
        Property("hasUniqueValue", BooleanType),
        Property("hidden", BooleanType),
        Property("hubspotDefined", BooleanType),
        Property("modificationMetadata", StringType),
        Property("formField", BooleanType),
        Property("hubspot_object", StringType),
        Property("showCurrencySymbol", StringType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """
        Returns api records with added columns
        """

        try:
            row["hubspot_object"] = "note"
        except:
            pass

        return super().post_process(row, context)

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """
        Merges all the property stream data into a single property table
        """
        
        property_ticket = PropertyTicketStream(self._tap, schema={"properties": {}})
        property_deal = PropertyDealStream(self._tap, schema={"properties": {}})
        property_contact = PropertyContactStream(self._tap, schema={"properties": {}})
        property_company = PropertyCompanyStream(self._tap, schema={"properties": {}})
        property_product = PropertyProductStream(self._tap, schema={"properties": {}})
        property_lineitem = PropertyLineItemStream(self._tap, schema={"properties": {}})
        property_email = PropertyEmailStream(self._tap, schema={"properties": {}})
        property_postalmail = PropertyPostalMailStream(
            self._tap, schema={"properties": {}}
        )
        property_call = PropertyCallStream(self._tap, schema={"properties": {}})
        property_meeting = PropertyMeetingStream(self._tap, schema={"properties": {}})
        property_task = PropertyTaskStream(self._tap, schema={"properties": {}})
        property_communication = PropertyCommunicationStream(
            self._tap, schema={"properties": {}}
        )
        property_records = (
            list(property_ticket.get_records(context))
            + list(property_deal.get_records(context))
            + list(property_contact.get_records(context))
            + list(property_company.get_records(context))
            + list(property_product.get_records(context))
            + list(property_lineitem.get_records(context))
            + list(property_email.get_records(context))
            + list(property_postalmail.get_records(context))
            + list(property_call.get_records(context))
            + list(property_meeting.get_records(context))
            + list(property_task.get_records(context))
            + list(property_communication.get_records(context))
            + list(super().get_records(context))
        )

        return property_records


class CompanyStream(HubspotStream):

    """
    https://developers.hubspot.com/docs/api/crm/companies
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, properties, createdAt, updatedAt, archived
              """

    name = "companies"
    path = "/objects/companies"
    primary_keys = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class DealStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/deals
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, properties, createdAt, updatedAt, archived
              """

    name = "deals"
    path = "/objects/deals"
    primary_keys = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("amount", StringType),
                Property("createdDate", StringType),
                Property("closedDate", StringType),
                Property("dealname", StringType),
                Property("dealstage", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hubspot_owner_id", StringType),
                Property("pipeline", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class FeedbackSubmissionsStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/feedback-submissions
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, properties, createdAt, updatedAt, archived
              """

    name = "feedbacksubmissions"
    path = "/objects/feedback_submissions"
    primary_keys = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("hs_content", StringType),
                Property("hs_ingestion_id", StringType),
                Property("hs_response_group", StringType),
                Property("hs_submission_name", StringType),
                Property("hs_survey_channel", StringType),
                Property("hs_survey_id", StringType),
                Property("hs_survey_name", StringType),
                Property("hs_survey_type", StringType),
                Property("hs_value", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class LineItemStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/line-items
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, properties, createdAt, updatedAt, archived
              """

    name = "lineitems"
    path = "/objects/line_items"
    primary_keys = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class ProductStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/products
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                id, properties, createdAt, updatedAt, archived
              """

    name = "product"
    path = "/objects/products"
    primary_keys = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class TicketStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/tickets
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "ticket"
    path = "/objects/tickets"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class QuoteStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/quotes
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "quote"
    path = "/objects/quotes"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class GoalStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/goals
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "goal"
    path = "/objects/goal_targets"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class CallStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/calls
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "call"
    path = "/objects/calls"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_call_body", StringType),
                Property("hs_call_duration", StringType),
                Property("hs_call_from_number", StringType),
                Property("hs_call_recording_url", StringType),
                Property("hs_call_status", StringType),
                Property("hs_call_title", StringType),
                Property("hs_call_to_number", StringType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class CommunicationStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/communications
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "communication"
    path = "/objects/Communications"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_communication_body", StringType),
                Property("hs_communication_channel_type", StringType),
                Property("hs_communication_logged_from", StringType),
                Property("hs_lastmodifieddate", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class EmailStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/email
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "email"
    path = "/objects/emails"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class MeetingStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/meetings
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "meeting"
    path = "/objects/meetings"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_internal_meeting_notes", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_meeting_body", StringType),
                Property("hs_meeting_end_time", StringType),
                Property("hs_meeting_external_url", StringType),
                Property("hs_meeting_location", StringType),
                Property("hs_meeting_outcome", StringType),
                Property("hs_meeting_start_time", StringType),
                Property("hs_meeting_title", StringType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class NoteStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/notes
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "note"
    path = "/objects/notes"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_note_body", StringType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class PostalMailStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/postal-mail
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "postalmail"
    path = "/objects/postal_mail"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_postal_mail_body", StringType),
            ),
        ),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("archived", BooleanType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results


class TaskStream(HubspotStream):
    """
    https://developers.hubspot.com/docs/api/crm/tasks
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    columns = """
                properties
              """

    name = "task"
    path = "/objects/tasks"
    primary_keys = ["properties"]

    schema = PropertiesList(
        Property("id", IntegerType),
        Property(
            "properties",
            ObjectType(
                Property("createdate", StringType),
                Property("hs_lastmodifieddate", StringType),
                Property("hs_task_body", StringType),
                Property("hs_task_priority", StringType),
                Property("hs_task_status", StringType),
                Property("hs_task_subject", StringType),
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
        """
        Returns an updated path which includes the api version
        """
        base_url = "https://api.hubapi.com/crm/v3"
        return base_url

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp_json = response.json()

        if isinstance(resp_json, list):
            results = resp_json
        elif resp_json.get("results") is not None:
            results = resp_json["results"]
        else:
            results = resp_json

        yield from results
