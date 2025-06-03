"""tap-hubspot tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_hubspot import streams


class TapHubspot(Tap):
    """tap-hubspot is a Singer tap for Hubspot."""

    name = "tap-hubspot"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=False,
            description="Token to authenticate against the API service",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=False,
            description="The OAuth app client ID.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=False,
            description="The OAuth app client secret.",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            required=False,
            description="The OAuth app refresh token.",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest record date to sync",
        ),
        th.Property(
            "end_date",
            th.DateTimeType,
            description="Latest record date to sync",
        ),
        th.Property(
            "enabled_hubspot_pull_web_events",
            th.BooleanType,
            default=False,
            description="Enable syncing of web events for contacts (incremental, only for modified contacts)",
        ),
        th.Property(
            "enabled_hubspot_pull_global_web_events",
            th.BooleanType,
            default=False,
            description="Enable syncing of all web events globally (comprehensive, but may be slower)",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.HubspotStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ContactStream(self),
            streams.CompanyStream(self),
            streams.DealStream(self),
            streams.EmailEventsStream(self),
            streams.WebEventsStream(self),
            streams.FormSubmissionsStream(self),
        ]


if __name__ == "__main__":
    TapHubspot.cli()
