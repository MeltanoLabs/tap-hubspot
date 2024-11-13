"""REST client handling, including HubspotStream base class."""

from __future__ import annotations

import datetime
import sys
from typing import Any, Callable, Iterable

import requests
from singer_sdk import typing as th
from singer_sdk._singerlib.utils import strptime_to_utc
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams.core import REPLICATION_INCREMENTAL

from tap_hubspot.auth import HubSpotOAuthAuthenticator

if sys.version_info < (3, 11):
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]


class HubspotStream(RESTStream):
    """tap-hubspot stream class."""

    records_jsonpath = "$[results][*]"
    next_page_token_jsonpath = "$[paging][next][after]"
    limit = 100

    @property
    def url_base(self) -> str:
        """Returns base url"""
        return "https://api.hubapi.com"

    @cached_property
    def authenticator(self) -> _Auth:
        """Return a new authenticator object.

        Depending on the configuration, this will return either a BearerTokenAuthenticator or a HubSpotOAuthAuthenticator.
        """
        if (
            refresh_token := self.config.get("refresh_token")
        ) and refresh_token != "None":
            return HubSpotOAuthAuthenticator(
                self,
                auth_endpoint="https://api.hubapi.com/oauth/v1/token",
            )

        return BearerTokenAuthenticator(
            self,
            token=self.config.get("access_token"),
        )

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        params: dict = {}
        params["limit"] = self.limit
        if next_page_token:
            params["after"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params


class DynamicHubspotStream(HubspotStream):
    """DynamicHubspotStream"""

    def _get_datatype(self, data_type: str) -> th.JSONTypeHelper:
        return th.StringType

    def properties_schema(self) -> list[th.Property]:
        return [
            th.Property(prop, self._get_datatype(data_type))
            for prop, data_type in self.hs_properties.items()
        ]

    @cached_property
    def schema(self) -> dict:
        self.hs_properties = self._get_available_properties()
        schema = th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property(
                "properties",
                th.ObjectType(*self.properties_schema()),
            ),
            th.Property("createdAt", th.DateTimeType),
            th.Property("updatedAt", th.DateTimeType),
            th.Property("archived", th.BooleanType),
        )
        return schema.to_dict()

    def _get_available_properties(self) -> dict[str, str]:
        session = requests.Session()
        session.auth = self.authenticator
        object_name = self.path.split("/")[-1]

        resp = session.get(
            f"https://api.hubapi.com/crm/v3/properties/{object_name}",
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return {prop["name"]: prop["type"] for prop in results}

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        if self.hs_properties:
            params["properties"] = ",".join(self.hs_properties)
        return params


class DynamicIncrementalHubspotStream(DynamicHubspotStream):
    """DynamicIncrementalHubspotStream"""

    cursor_position = None
    start_of_sync = datetime.datetime.now(tz=datetime.timezone.utc)

    def _is_incremental_search(self, context: dict | None) -> bool:
        return (
            self.replication_method == REPLICATION_INCREMENTAL
            and self.get_starting_replication_key_value(context)
            and hasattr(self, "incremental_path")
            and self.incremental_path
        )

    @cached_property
    def schema(self) -> dict:
        self.hs_properties = self._get_available_properties()
        schema = th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property(
                "properties",
                th.ObjectType(*self.properties_schema()),
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
        context: dict | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        if self._is_incremental_search(context):
            return {}
        return super().get_url_params(context, next_page_token)

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        if self.replication_key:
            val = None
            if props := row.get("properties"):
                val = props[self.replication_key]
                # skip records that are newer than the start of the sync
                if val > self.start_of_sync.isoformat():
                    return None
            row[self.replication_key] = val
        return row

    def prepare_request(
        self,
        context: dict | None,
        next_page_token: str | None,
    ) -> requests.PreparedRequest:
        if self._is_incremental_search(context):
            # Search endpoints use POST request
            self.path = self.incremental_path
            self.rest_method = "POST"
        return super().prepare_request(context, next_page_token)

    def prepare_request_payload(
        self,
        context: dict | None,
        next_page_token: str | None,
    ) -> dict | None:
        body = {}
        if self._is_incremental_search(context):
            # Only filter in case we have a value to filter on
            # https://developers.hubspot.com/docs/api/crm/search
            if self.cursor_position is None:
                self.cursor_position = datetime.datetime.fromisoformat(
                    self.get_starting_replication_key_value(context),
                )
            if next_page_token:
                # Hubspot wont return more than 10k records so when we hit 10k we
                # need to reset our epoch to most recent and not send the next_page_token
                if int(next_page_token) + self.limit >= 10000:
                    self.cursor_position = strptime_to_utc(
                        self.get_context_state(context)
                        .get("progress_markers")
                        .get("replication_key_value"),
                    )
                else:
                    body["after"] = next_page_token

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
                                    "value": self.timestamp_to_milliseconds(
                                        self.cursor_position
                                    ),
                                },
                                {
                                    "propertyName": self.replication_key,
                                    "operator": "LTE",
                                    "value": self.timestamp_to_milliseconds(
                                        self.start_of_sync
                                    ),
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
                    "limit": self.limit,
                    "properties": list(self.hs_properties),
                },
            )

        return body

    def timestamp_to_milliseconds(self, value: datetime.datetime) -> str:
        return str(int(value.timestamp() * 1000))


class HubspotAnalyticsStream(HubspotStream):
    """HubspotAnalyticsStream"""

    records_jsonpath = "$[*]"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        params = {}
        if replication_key_value := self.get_starting_replication_key_value(context):
            # Retrieving last 30 days of data just to be sure
            params["start"] = (
                datetime.datetime.strptime(replication_key_value, "%Y-%m-%d")
                - datetime.timedelta(days=30)
            ).strftime("%Y-%m-%d")

        return params

    def get_records(self, context: dict[str, Any] | None) -> Iterable[dict[str, Any]]:
        rows = super().get_records(context)
        for row in rows:
            for date, breakdowns in row.items():
                for breakdown in breakdowns:
                    breakdown["date"] = date
                    yield breakdown
