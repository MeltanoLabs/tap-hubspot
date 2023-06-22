"""tap-hubspot tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_hubspot import streams


class TapHubspot(Tap):
    """tap-hubspot tap class."""

    name = "tap-hubspot"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.HubspotStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ListsStream(self),
            streams.UsersStream(self),
            streams.OwnersStream(self),
            streams.TicketPipelineStream(self),
            streams.DealPipelineStream(self),
            streams.EmailSubscriptionStream(self),
            streams.PropertyNotesStream(self),
        ]


if __name__ == "__main__":
    TapHubspot.cli()
