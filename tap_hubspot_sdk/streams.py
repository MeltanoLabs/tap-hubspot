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


class AccountStream(HubspotStream):
    columns = """

              """

    name = "account"
    path = "/query?q=SELECT+{}+from+Account".format(columns)
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "incremental"

    schema = PropertiesList(
        Property("Id", StringType),


    ).to_dict()

    def get_url_params(
            self,
            context: dict | None,  # noqa: ARG002
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


