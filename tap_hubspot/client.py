"""REST client handling, including HubspotStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable

import requests
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream
from singer_sdk import typing as th

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

from singer_sdk.authenticators import BearerTokenAuthenticator
from tap_hubspot.auth import HubSpotOAuthAuthenticator

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]


class HubspotStream(RESTStream):
    """tap-hubspot stream class."""

    @property
    def url_base(self) -> str:
        """
        Returns base url
        """
        return "https://api.hubapi.com/"

    records_jsonpath = "$[*]"  # Or override `parse_response`.

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"

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
        else:
            return BearerTokenAuthenticator(
                self,
                token=self.config.get("access_token"),
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
        previous_token: t.Any | None,
    ) -> t.Any | None:
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
            params["after"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

class DynamicHubspotStream(HubspotStream):
    """DynamicHubspotStream"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_datatype(self, data_type: str) -> th.JSONTypeHelper:
        # TODO: consider typing more precisely
        return th.StringType()

    @cached_property
    def schema(self) -> dict:
        """Return a draft JSON schema for this stream."""
        hs_props = []
        self.hs_properties = self._get_available_properties()
        for name, type in self.hs_properties.items():
            hs_props.append(
                th.Property(name, self._get_datatype(type))
            )
        return th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property(
                "properties", th.ObjectType(*hs_props),
            ),
            th.Property("createdAt", th.StringType),
            th.Property("updatedAt", th.StringType),
            th.Property("archived", th.BooleanType),
        ).to_dict()

    def _get_available_properties(self) -> dict[str, str]:
        session = requests.Session()
        session.auth = self.authenticator

        resp = session.get(
            f"https://api.hubapi.com/crm/v3/properties/{self.name}",
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return {prop["name"]: prop["type"] for prop in results}

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
        params = super().get_url_params(context, next_page_token)
        if self.hs_properties:
            params["properties"] = ",".join(self.hs_properties)
        return params
