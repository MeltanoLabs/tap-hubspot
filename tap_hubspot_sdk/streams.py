"""Stream type classes for tap-hubspot-sdk."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_hubspot_sdk.client import HubspotStream

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType


class ListsStream(HubspotStream):

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
        Property("properties", 
                 ObjectType(Property("lastmodifieddate", StringType),
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
                            )
                            
                ),
        Property("form-submissions", ArrayType(StringType)),
        Property("identity-profiles", ArrayType(StringType)),
        Property("merge-audits", ArrayType(StringType)),
        Property("addedAt", StringType),

    ).to_dict()

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_1", "")
        base_url = "https://api.hubapi.com/contacts/{}".format(version)
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

        params["property"] = "message","email","city","company","createddate","firstname","hs_all_contact_vids","hs_date_entered_lead","hs_marketable_reason_id","hs_is_unworked","hs_marketable_until_renewal","hs_latest_source_timestamp","hs_marketable_reason_type","hs_marketable_status","hs_is_contact","hs_email_domain","hs_pipeline","hs_sequences_actively_enrolled_count","hs_object_id","hs_time_in_lead","num_conversion_events","num_unique_conversion_events","lastname","hs_analytics_num_page_views","hs_analytics_num_event_completions","hs_analytics_first_timestamp","hs_social_twitter_clicks","hs_analytics_num_visits","twitterprofilephoto","twitterhandle","hs_analytics_source_data_2","hs_social_facebook_clicks","hs_analytics_source","hs_analytics_source_data_1","hs_latest_source","hs_latest_source_data_1","hs_latest_source_data_2","hs_social_google_plus_clicks","hs_social_num_broadcast_clicks","state","hs_social_linkedin_clicks","hs_lifecyclestage_lead_date","hs_analytics_revenue","hs_analytics_average_page_views","website","lifecyclestage","jobtitle"
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
    https://legacydocs.hubspot.com/docs/methods/
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
    #replication_key = "LastModifiedDate"
    #replication_method = "incremental"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("email", StringType),
        Property("roleIds", ArrayType(StringType)),
        Property("primaryteamid", StringType),

    ).to_dict()

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/settings/{}".format(version)
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
    https://legacydocs.hubspot.com/docs/methods/owners/get_owners
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        Property("stages", StringType),
        Property("objectType", StringType),
        Property("objectTypeId", StringType),
        Property("pipelineId", StringType),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("default", StringType),

    ).to_dict()

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_1", "")
        base_url = "https://api.hubapi.com/crm-pipelines/{}".format(version)
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
        Property("stages", StringType),
        Property("objectType", StringType),
        Property("objectTypeId", StringType),
        Property("pipelineId", StringType),
        Property("createdAt", StringType),
        Property("updatedAt", StringType),
        Property("default", StringType),

    ).to_dict()

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_1", "")
        base_url = "https://api.hubapi.com/crm-pipelines/{}".format(version)
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
        Property("internal", StringType),
        Property("category", StringType),
        Property("channel", StringType),
        Property("internalName", StringType),
        Property("businessUnitId", StringType),

    ).to_dict()

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_1", "")
        base_url = "https://api.hubapi.com/email/public/{}".format(version)
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
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        
        row["hubspot_object"] = "ticket"
        
        return super().post_process(row, context)  

class PropertyDealStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyContactStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyCompanyStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyProductStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "product"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyLineItemStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "line_item"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyEmailStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "email"
        except:
            pass
        
        return super().post_process(row, context)  

class PropertyPostalMailStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "postal_mail"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyCallStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "call"
        except:
            pass
        
        return super().post_process(row, context)                                   

class PropertyMeetingStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "meeting"
        except:
            pass
        
        return super().post_process(row, context)
    
class PropertyTaskStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "task"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyCommunicationStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "communication"
        except:
            pass
        
        return super().post_process(row, context)

class PropertyNotesStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods
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
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
        try:
            row["hubspot_object"] = "note"
        except:
            pass
        
        return super().post_process(row, context)

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        property_ticket = PropertyTicketStream(
            self._tap, schema={"properties": {}}
        )
        property_deal = PropertyDealStream(
            self._tap, schema={"properties": {}}
        )
        property_contact = PropertyContactStream(
            self._tap, schema={"properties": {}}
        )
        property_company = PropertyCompanyStream(
            self._tap, schema={"properties": {}}
        )
        property_product = PropertyProductStream(
            self._tap, schema={"properties": {}}
        )
        property_lineitem = PropertyLineItemStream(
            self._tap, schema={"properties": {}}
        )
        property_email = PropertyEmailStream(
            self._tap, schema={"properties": {}}
        )
        property_postalmail = PropertyPostalMailStream(
            self._tap, schema={"properties": {}}
        )
        property_call = PropertyCallStream(
            self._tap, schema={"properties": {}}
        )
        property_meeting = PropertyMeetingStream(
            self._tap, schema={"properties": {}}
        )
        property_task = PropertyTaskStream(
            self._tap, schema={"properties": {}}
        )
        property_communication = PropertyCommunicationStream(
            self._tap, schema={"properties": {}}
        )
        property_records = list(property_ticket.get_records(context)) + list(property_deal.get_records(context)) + list(property_contact.get_records(context)) + list(property_company.get_records(context)) + list(property_product.get_records(context)) + list(property_lineitem.get_records(context)) + list(property_email.get_records(context)) + list(property_postalmail.get_records(context)) + list(property_call.get_records(context)) + list(property_meeting.get_records(context)) + list(property_task.get_records(context)) + list(property_communication.get_records(context)) + list(super().get_records(context))
            
        return property_records
    
class AssociationContactCompanyTypeStream(HubspotStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "contactcompanytype"
    path = "/associations/contact/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("from_object_type", StringType),
        Property("to_object_type", StringType),
        Property("category", StringType),
        Property("typeId", IntegerType),
        Property("label", StringType),

    ).to_dict()

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
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
    
class AssociationContactCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "contactcompanylabel"
    path = "/associations/contact/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "contact"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationDealContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "dealcontacttype"
    path = "/associations/deal/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "deal"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationDealContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "dealcontactlabel"
    path = "/associations/deal/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "deal"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationDealCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "dealcompanytype"
    path = "/associations/deal/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "deal"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationDealCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "dealcompanylabel"
    path = "/associations/deal/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "deal"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketcontacttype"
    path = "/associations/ticket/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketcontactlabel"
    path = "/associations/ticket/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketcompanytype"
    path = "/associations/ticket/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)
    
class AssociationTicketCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketcompanylabel"
    path = "/associations/ticket/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)                                    
    
class AssociationTicketDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketdealtype"
    path = "/associations/ticket/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)
    
class AssociationTicketDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketdeallabel"
    path = "/associations/ticket/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)            

class AssociationTicketCommunicationTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketcommunicationtype"
    path = "/associations/ticket/communication/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "communication"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketCommunicationLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketcommunicationlabel"
    path = "/associations/ticket/communication/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "communication"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketCallTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketcalltype"
    path = "/associations/ticket/call/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "call"
        except:
            pass
        
        return super().post_process(row, context)
    
class AssociationTicketCallLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketcalllabel"
    path = "/associations/ticket/call/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "call"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketMeetingTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketmeetingtype"
    path = "/associations/ticket/meeting/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "meeting"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketMeetingLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketmeetinglabel"
    path = "/associations/ticket/meeting/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "meeting"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketNoteTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketnotetype"
    path = "/associations/ticket/note/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "note"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketNoteLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketnotelabel"
    path = "/associations/ticket/note/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "note"
        except:
            pass
        
        return super().post_process(row, context)                                
    
class AssociationTicketTaskTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "tickettasktype"
    path = "/associations/ticket/task/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "task"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketTaskLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "tickettasklabel"
    path = "/associations/ticket/task/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "task"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketEmailTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketemailtype"
    path = "/associations/ticket/email/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "email"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketEmailLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketemaillabel"
    path = "/associations/ticket/email/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "email"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketPostalMailTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "ticketpostalmailtype"
    path = "/associations/ticket/postal_mail/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "postal_mail"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTicketPostalMailLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "ticketpostalmaillabel"
    path = "/associations/ticket/postal_mail/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "ticket"
            row["to_object_type"] = "postal_mail"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationLineItemDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "lineitemdealtype"
    path = "/associations/line_item/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "line_item"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationLineItemDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "lineitemdeallabel"
    path = "/associations/line_item/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "line_item"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCommunicationContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "communicationcontacttype"
    path = "/associations/communication/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "communication"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCommunicationContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "communicationcontactlabel"
    path = "/associations/communication/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "communication"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCommunicationCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "communicationcompanytype"
    path = "/associations/communication/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "communication"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCommunicationCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "communicationcompanylabel"
    path = "/associations/communication/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "communication"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCommunicationDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "communicationdealtype"
    path = "/associations/communication/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "communication"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AsociationCommunicationDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "communicationdeallabel"
    path = "/associations/communication/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "communication"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCallContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "callcontacttype"
    path = "/associations/call/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "call"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCallContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "callcontactlabel"
    path = "/associations/call/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "call"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCallCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "callcompanytype"
    path = "/associations/call/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "call"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCallCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "callcompanylabel"
    path = "/associations/call/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "call"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCallDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "calldealtype"
    path = "/associations/call/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "call"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationCallDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "calldeallabel"
    path = "/associations/call/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "call"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)
    
class AssociationEmailContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "emailcontacttype"
    path = "/associations/email/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "email"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationEmailContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "emailcontactlabel"
    path = "/associations/email/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "email"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationEmailCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "emailcompanytype"
    path = "/associations/email/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "email"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationEmailCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "emailcompanylabel"
    path = "/associations/email/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "email"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationEmailDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "emaildealtype"
    path = "/associations/email/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "email"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationEmailDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "emaildeallabel"
    path = "/associations/email/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "email"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationMeetingContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "meetingcontacttype"
    path = "/associations/meeting/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "meeting"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)                            
                                                                                    
class AssociationMeetingContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "meetingcontactlabel"
    path = "/associations/meeting/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "meeting"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationMeetingCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "meetingcompanytype"
    path = "/associations/meeting/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "meeting"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationMeetingCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "meetingcompanylabel"
    path = "/associations/meeting/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "meeting"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationMeetingDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "meetingdealtype"
    path = "/associations/meeting/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "meeting"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationMeetingDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "meetingdeallabel"
    path = "/associations/meeting/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "meeting"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)
    
class AssociationNoteContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "notecontacttype"
    path = "/associations/note/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "note"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationNoteContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "notecontactlabel"
    path = "/associations/note/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "note"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationNoteCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "notecompanytype"
    path = "/associations/note/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "note"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationNoteCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "notecompanylabel"
    path = "/associations/note/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "note"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssoxationNoteDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "notedealtype"
    path = "/associations/note/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "note"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationNoteDealLabel(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "notedeallabel"
    path = "/associations/note/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "note"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTaskContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "taskcontacttype"
    path = "/associations/task/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "task"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTaskContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "taskcontactlabel"
    path = "/associations/task/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "task"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTaskCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "taskcompanytype"
    path = "/associations/task/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "task"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTaskCompanyLabelstream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "taskcompanystream"
    path = "/associations/task/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "task"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTaskDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "taskdealtype"
    path = "/associations/task/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "task"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationTaskDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "taskdeallabel"
    path = "/associations/task/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "task"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationPostalMailContactTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "postalmalicontacttype"
    path = "/associations/postal_mail/contact/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "postal_mail"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationPostalMailContactLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "postalmailcontactlabel"
    path = "/associations/postal_mail/contact/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "postal_mail"
            row["to_object_type"] = "contact"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationPostalMailCompanyTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "postalmailcompanytype"
    path = "/associations/postal_mail/company/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "postal_mail"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationPostalMailCompanyLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "postalmailcompanylabel"
    path = "/associations/postal_mail/company/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "postal_mail"
            row["to_object_type"] = "company"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationPostalMailDealTypeStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                id, name
              """

    name = "postalmaildealtype"
    path = "/associations/postal_mail/deal/types?fields={}".format(columns)
    primary_keys = ["id"]
    replication_key = "id"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_3", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "postal_mail"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

class AssociationPostalMailDealLabelStream(AssociationContactCompanyTypeStream):

    """
    https://legacydocs.hubspot.com/docs/methods/crm-associations/get-associations
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
                category, typeId, label
              """

    name = "association_type"
    path = "/associations/postal_mail/deal/labels?fields={}".format(columns)
    primary_keys = ["typeId"]
    replication_key = "typeId"
    replication_method = "incremental"

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version_4", "")
        base_url = "https://api.hubapi.com/crm/{}".format(version)
        return base_url
    
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        try:
            row["from_object_type"] = "postal_mail"
            row["to_object_type"] = "deal"
        except:
            pass
        
        return super().post_process(row, context)

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:

        """
        We have type and label api for id and name column and type and label api for category, typeId, and label columns 
        We can get data from these api and merge these columns from type and label api with merge_dicts function, we can add the records from merge_dicts function to get the output
        """

        contact_company_type = AssociationContactCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        contact_company_label = AssociationContactCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        deal_contact_type = AssociationDealContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        deal_contact_label = AssociationDealContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        deal_company_type = AssociationDealCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        deal_company_label = AssociationDealCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_contact_type = AssociationTicketContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_contact_label = AssociationTicketContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_company_type = AssociationTicketCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_company_label = AssociationTicketCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_deal_type = AssociationTicketDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_deal_label = AssociationTicketDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_communication_type = AssociationTicketCommunicationTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_communication_label = AssociationTicketCommunicationLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_call_type = AssociationTicketCallTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_call_label = AssociationTicketCallLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_meeting_type = AssociationTicketMeetingTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_meeting_label = AssociationTicketMeetingLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_note_type = AssociationTicketNoteTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_note_label = AssociationTicketNoteLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_task_type = AssociationTicketTaskTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_task_label = AssociationTicketTaskLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_email_type = AssociationTicketEmailTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_email_label = AssociationTicketEmailLabelStream(
            self._tap, schema={"properties": {}}
        )
        ticket_postal_type = AssociationTicketPostalMailTypeStream(
            self._tap, schema={"properties": {}}
        )
        ticket_postal_label = AssociationTicketPostalMailLabelStream(
            self._tap, schema={"properties": {}}
        )
        line_deal_type = AssociationLineItemDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        line_deal_label = AssociationLineItemDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        communication_contact_type = AssociationCommunicationContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        communication_contact_label = AssociationCommunicationContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        communication_company_type = AssociationCommunicationCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        communication_company_label = AssociationCommunicationCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        communication_deal_type = AssociationCommunicationDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        communication_deal_label = AsociationCommunicationDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        call_contact_type = AssociationCallContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        call_contact_label = AssociationCallContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        call_company_type = AssociationCallCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        call_company_label = AssociationCallCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        call_deal_type = AssociationCallDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        call_deal_label = AssociationCallDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        email_contact_type = AssociationEmailContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        email_contact_label = AssociationEmailContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        email_company_type = AssociationEmailCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        email_company_label = AssociationEmailCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        email_deal_type = AssociationEmailDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        email_deal_label = AssociationEmailDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        meeting_contact_type = AssociationMeetingContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        meeting_contact_label = AssociationMeetingContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        meeting_company_type = AssociationMeetingCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        meeting_company_label = AssociationMeetingCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        meeting_deal_type = AssociationMeetingDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        meeting_deal_label = AssociationMeetingDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        note_contact_type = AssociationNoteContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        note_contact_label = AssociationNoteContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        note_company_type = AssociationNoteCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        note_company_label = AssociationNoteCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        note_deal_type = AssoxationNoteDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        note_deal_label = AssociationNoteDealLabel(
            self._tap, schema={"properties": {}}
        )
        task_contact_type = AssociationTaskContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        task_contact_label = AssociationTaskContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        task_company_type = AssociationTaskCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        task_company_label = AssociationTaskCompanyLabelstream(
            self._tap, schema={"properties": {}}
        )
        task_deal_type = AssociationTaskDealTypeStream(
            self._tap, schema={"properties": {}}
        )
        task_deal_label = AssociationTaskDealLabelStream(
            self._tap, schema={"properties": {}}
        )
        postal_contact_type = AssociationPostalMailContactTypeStream(
            self._tap, schema={"properties": {}}
        )
        postal_contact_label = AssociationPostalMailContactLabelStream(
            self._tap, schema={"properties": {}}
        )
        postal_company_type = AssociationPostalMailCompanyTypeStream(
            self._tap, schema={"properties": {}}
        )
        postal_company_label = AssociationPostalMailCompanyLabelStream(
            self._tap, schema={"properties": {}}
        )
        postal_deal_type = AssociationPostalMailDealTypeStream(
            self._tap, schema={"properties": {}}
        )

        contact_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(contact_company_type.get_records(context)),
                list(contact_company_label.get_records(context))
            )
        ]

        deal_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(deal_contact_type.get_records(context)),
                list(deal_contact_label.get_records(context))
            )
        ]

        deal_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(deal_company_type.get_records(context)),
                list(deal_company_label.get_records(context))
            )
        ]

        ticket_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_contact_type.get_records(context)),
                list(ticket_contact_label.get_records(context))
            )
        ]

        ticket_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_company_type.get_records(context)),
                list(ticket_company_label.get_records(context))
            )
        ]

        ticket_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_deal_type.get_records(context)),
                list(ticket_deal_label.get_records(context))
            )
        ]

        ticket_communication_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_communication_type.get_records(context)),
                list(ticket_communication_label.get_records(context))
            )
        ]

        ticket_call_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_call_type.get_records(context)),
                list(ticket_call_label.get_records(context))
            )
        ]

        ticket_meeting_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_meeting_type.get_records(context)),
                list(ticket_meeting_label.get_records(context))
            )
        ]

        ticket_note_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_note_type.get_records(context)),
                list(ticket_note_label.get_records(context))
            )
        ]

        ticket_task_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_task_type.get_records(context)),
                list(ticket_task_label.get_records(context))
            )
        ]

        ticket_email_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_email_type.get_records(context)),
                list(ticket_email_label.get_records(context))
            )
        ]

        ticket_postal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(ticket_postal_type.get_records(context)),
                list(ticket_postal_label.get_records(context))
            )
        ]

        line_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(line_deal_type.get_records(context)),
                list(line_deal_label.get_records(context))
            )
        ]

        communication_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(communication_contact_type.get_records(context)),
                list(communication_contact_label.get_records(context))
            )
        ]

        communication_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(communication_company_type.get_records(context)),
                list(communication_company_label.get_records(context))
            )
        ]

        communication_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(communication_deal_type.get_records(context)),
                list(communication_deal_label.get_records(context))
            )
        ]

        call_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(call_contact_type.get_records(context)),
                list(call_contact_label.get_records(context))
            )
        ]

        call_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(call_company_type.get_records(context)),
                list(call_company_label.get_records(context))
            )
        ]

        call_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(call_deal_type.get_records(context)),
                list(call_deal_label.get_records(context))
            )
        ]

        email_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(email_contact_type.get_records(context)),
                list(email_contact_label.get_records(context))
            )
        ]

        email_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(email_company_type.get_records(context)),
                list(email_company_label.get_records(context))
            )
        ]

        email_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(email_deal_type.get_records(context)),
                list(email_deal_label.get_records(context))
            )
        ]

        meeting_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(meeting_contact_type.get_records(context)),
                list(meeting_contact_label.get_records(context))
            )
        ]

        meeting_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(meeting_company_type.get_records(context)),
                list(meeting_company_label.get_records(context))
            )
        ]

        meeting_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(meeting_deal_type.get_records(context)),
                list(meeting_deal_label.get_records(context))
            )
        ]

        note_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(note_contact_type.get_records(context)),
                list(note_contact_label.get_records(context))
            )
        ]

        note_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(note_company_type.get_records(context)),
                list(note_company_label.get_records(context))
            )
        ]

        note_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(note_deal_type.get_records(context)),
                list(note_deal_label.get_records(context))
            )
        ]

        task_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(task_contact_type.get_records(context)),
                list(task_contact_label.get_records(context))
            )
        ]

        task_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(task_company_type.get_records(context)),
                list(task_company_label.get_records(context))
            )
        ]

        task_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(task_deal_type.get_records(context)),
                list(task_deal_label.get_records(context))
            )
        ]

        postal_contact_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(postal_contact_type.get_records(context)),
                list(postal_contact_label.get_records(context))
            )
        ]

        postal_company_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(postal_company_type.get_records(context)),
                list(postal_company_label.get_records(context))
            )
        ]

        postal_deal_records = [
            self.merge_dicts(x, y)
            for x, y in zip(
                list(postal_deal_type.get_records(context)),
                list(super().get_records(context))
            )
        ]

        association_records  = contact_company_records + deal_contact_records + deal_company_records + ticket_contact_records + ticket_company_records + ticket_deal_records + ticket_communication_records + ticket_call_records + ticket_meeting_records + ticket_note_records + ticket_task_records + ticket_email_records + ticket_postal_records + line_deal_records + communication_contact_records + communication_company_records + communication_deal_records + call_contact_records + call_company_records + call_deal_records + email_contact_records + email_company_records + email_deal_records + meeting_contact_records + meeting_company_records + meeting_deal_records + note_contact_records + note_company_records + note_deal_records + task_contact_records + task_company_records + task_deal_records + postal_contact_records + postal_company_records + postal_deal_records

        return association_records

    def merge_dicts(self, *dict_args):
        """
        Given any number of dictionaries, shallow copy and merge into a new dict,
        precedence goes to key-value pairs in latter dictionaries.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
                                                                            
                                                                                                        