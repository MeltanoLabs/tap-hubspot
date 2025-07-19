"""REST client handling, including HubspotStream base class."""

from __future__ import annotations

import datetime
import sys
import typing as t
from functools import cached_property
from http import HTTPStatus

import requests
from singer_sdk import typing as th
from singer_sdk._singerlib.utils import strptime_to_utc
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream
from singer_sdk.streams.core import REPLICATION_INCREMENTAL

from tap_hubspot.auth import HubSpotOAuthAuthenticator

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context
    from singer_sdk.pagination import BaseAPIPaginator

if sys.version_info < (3, 11):
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()

_Auth = t.Callable[[requests.PreparedRequest], requests.PreparedRequest]


class HubspotStream(RESTStream):
    """tap-hubspot stream class."""

    @property
    def url_base(self) -> str:
        """Returns base url."""
        return "https://api.hubapi.com/"

    records_jsonpath = "$[*]"  # Or override `parse_response`.

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @cached_property
    def authenticator(self) -> _Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        if "refresh_token" in self.config:
            return HubSpotOAuthAuthenticator(
                self,
                auth_endpoint="https://api.hubapi.com/oauth/v1/token",
            )
        return BearerTokenAuthenticator(
            self,
            token=self.config.get("access_token"),  # type: ignore[arg-type]
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        If the source API can make use of the `next_page_token_jsonpath`
        attribute, or it contains a `X-Next-Page` header in the response
        then you can remove this method.

        If you need custom pagination that uses page numbers, "next" links, or
        other approaches, please read the guide: https://sdk.meltano.com/en/v0.25.0/guides/pagination-classes.html.

        Returns:
            A pagination helper instance.
        """
        return super().get_new_paginator()

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: int | None,  # noqa: ARG002
    ) -> int | None:
        """Return a token for identifying next page or None if no more pages."""
        # If pagination is required, return a token which can be used to get the
        #       next page. If this is the final page, return "None" to end the
        #       pagination loop.
        resp_json = response.json()
        paging = resp_json.get("paging")

        if paging is not None:
            next_page_token = resp_json.get("paging", {}).get("next", {}).get("after")
        else:
            next_page_token = None
        return next_page_token

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: int | None,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        params["limit"] = 100
        if next_page_token:
            params["after"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

class PropertyStream(HubspotStream):
    """Property stream class."""

    schema = th.PropertiesList(
        th.Property("updatedAt", th.StringType),
        th.Property("createdAt", th.StringType),
        th.Property("name", th.StringType),
        th.Property("label", th.StringType),
        th.Property("type", th.StringType),
        th.Property("fieldType", th.StringType),
        th.Property("description", th.StringType),
        th.Property("groupName", th.StringType),
        th.Property(
            "options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("label", th.StringType),
                    th.Property("description", th.StringType),
                    th.Property("value", th.StringType),
                    th.Property("displayOrder", th.IntegerType),
                    th.Property("hidden", th.BooleanType),
                ),
            ),
        ),
        th.Property("displayOrder", th.IntegerType),
        th.Property("calculated", th.BooleanType),
        th.Property("externalOptions", th.BooleanType),
        th.Property("hasUniqueValue", th.BooleanType),
        th.Property("hidden", th.BooleanType),
        th.Property("hubspotDefined", th.BooleanType),
        th.Property(
            "modificationMetadata",
            th.ObjectType(
                th.Property("readOnlyOptions", th.BooleanType),
                th.Property("readOnlyValue", th.BooleanType),
                th.Property("readOnlyDefinition", th.BooleanType),
                th.Property("archivable", th.BooleanType),
            ),
        ),
        th.Property("formField", th.BooleanType),
        th.Property("hubspot_object", th.StringType),
    ).to_dict()

    primary_keys = ("label",)
    records_jsonpath = "$[results][*]"

    @property
    def url_base(self) -> str:  # noqa: D102
        return "https://api.hubapi.com/crm/v3"

    @property
    def path(self) -> str:  # noqa: D102
        return f"/properties/{self.name}"

    def validate_response(self, response: requests.Response) -> None:  # noqa: D102
        if response.status_code == HTTPStatus.FORBIDDEN:
            self.logger.warning(self.response_error_message(response))
            self.logger.warning(
                "No properties available for object type '%s'",
                self.name,
            )
        else:
            super().validate_response(response)

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:  # noqa: D102
        if response.status_code == HTTPStatus.FORBIDDEN:
            return []

        return super().parse_response(response)

class DynamicHubspotStream(HubspotStream):
    """DynamicHubspotStream."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:  # noqa: D107
        super().__init__(*args, **kwargs)

    def _get_datatype(self, data_type: str) -> th.JSONTypeHelper:  # noqa: ARG002
        # TODO: consider typing more precisely  # noqa: TD002, TD003, FIX002
        return th.StringType()

    @cached_property
    def schema(self) -> dict:
        """Return a draft JSON schema for this stream."""
        hs_props = []
        self.hs_properties = self._get_available_properties()
        for name, prop_type in self.hs_properties.items():
            hs_props.append(
                th.Property(name, self._get_datatype(prop_type)),
            )
        schema = th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property(
                "properties",
                th.ObjectType(*hs_props),
            ),
            th.Property("createdAt", th.DateTimeType),
            th.Property("updatedAt", th.DateTimeType),
            th.Property("archived", th.BooleanType),
        )
        return schema.to_dict()

    def _get_available_properties(self) -> dict[str, str]:
        property_stream = PropertyStream(self._tap, self.name)
        results = property_stream.get_records(None)

        return {prop["name"]: prop["type"] for prop in results}

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
        if self.hs_properties:
            params["properties"] = ",".join(self.hs_properties)
        return params


class DynamicIncrementalHubspotStream(DynamicHubspotStream):
    """DynamicIncrementalHubspotStream."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:  # noqa: D107
        super().__init__(*args, **kwargs)

    def _is_incremental_search(self, context: Context | None) -> bool:
        return (
            self.replication_method == REPLICATION_INCREMENTAL  # type: ignore[return-value]
            and self.get_starting_replication_key_value(context)
            and hasattr(self, "incremental_path")
            and self.incremental_path
        )

    @cached_property
    def schema(self) -> dict:
        """Return a draft JSON schema for this stream."""
        hs_props = []
        self.hs_properties = self._get_available_properties()
        for name, prop_type in self.hs_properties.items():
            hs_props.append(
                th.Property(name, self._get_datatype(prop_type)),
            )
        schema = th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property(
                "properties",
                th.ObjectType(*hs_props),
            ),
            th.Property("createdAt", th.DateTimeType),
            th.Property("updatedAt", th.DateTimeType),
            th.Property("archived", th.BooleanType),
        )
        if self.replication_key:
            schema.append(
                th.Property(
                    self.replication_key,
                    th.DateTimeType,
                ),
            )
        return schema.to_dict()

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
        if self._is_incremental_search(context):
            return {}
        return super().get_url_params(context, next_page_token)

    def post_process(
        self,
        row: dict,
        context: Context | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Optional. This method gives developers an opportunity to "clean up" the results
        prior to returning records to the downstream tap - for instance: cleaning,
        renaming, or appending properties to the raw record result returned from the
        API.
        Developers may also return `None` from this method to filter out
        invalid or not-applicable records from the stream.

        Args:
            row: Individual record in the stream.
            context: Stream partition or context dictionary.

        Returns:
            The resulting record dict, or `None` if the record should be excluded.
        """
        if self.replication_key:
            val = None
            if props := row.get("properties"):
                val = props[self.replication_key]
            row[self.replication_key] = val
        return row

    def prepare_request(  # noqa: D102
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> requests.PreparedRequest:
        if self._is_incremental_search(context):
            # Search endpoints use POST request
            self.path = self.incremental_path  # type: ignore[attr-defined]
            self.http_method = "POST"
        return super().prepare_request(context, next_page_token)

    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Developers may override this method if the API requires a custom payload along
        with the request. (This is generally not required for APIs which use the
        HTTP 'GET' method.)

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.
        """
        body: dict[str, t.Any] = {}
        if self._is_incremental_search(context):
            # Only filter in case we have a value to filter on
            # https://developers.hubspot.com/docs/api/crm/search
            ts = datetime.datetime.fromisoformat(
                self.get_starting_replication_key_value(context),  # type: ignore[arg-type]
            )
            if next_page_token:
                # Hubspot wont return more than 10k records so when we hit 10k we
                # need to reset our epoch to most recent and not send the
                # next_page_token
                if int(next_page_token) + 100 >= 10000:  # noqa: PLR2004
                    ts = strptime_to_utc(
                        self.get_context_state(context)  # type: ignore[union-attr]
                        .get("progress_markers")
                        .get("replication_key_value"),
                    )
                else:
                    body["after"] = next_page_token
            epoch_ts = str(int(ts.timestamp() * 1000))

            body.update(
                {
                    "filterGroups": [
                        {
                            "filters": [
                                {
                                    "propertyName": self.replication_key,
                                    "operator": "GTE",
                                    # Timestamps need to be in milliseconds
                                    # https://legacydocs.hubspot.com/docs/faq/how-should-timestamps-be-formatted-for-hubspots-apis
                                    "value": epoch_ts,
                                },
                            ],
                        },
                    ],
                    "sorts": [
                        {
                            # This is inside the properties object
                            "propertyName": self.replication_key,
                            "direction": "ASCENDING",
                        },
                    ],
                    # Hubspot sets a limit of most 100 per request. Default is 10
                    "limit": 100,
                    "properties": list(self.hs_properties),
                },
            )

        return body
