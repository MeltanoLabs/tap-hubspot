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
    ).to_dict()

    def discover_streams(self) -> list[streams.HubspotStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.EmailStream(self),
            streams.EmailSubscriptionStream(self),
            streams.ProductStream(self),
            streams.TicketStream(self),
            streams.CallStream(self),
            streams.CommunicationStream(self),
            streams.CompanyStream(self),
            streams.ContactStream(self),
            streams.DealPipelineStream(self),
            streams.DealStream(self),
            streams.FeedbackSubmissionsStream(self),
            streams.FormStream(self),
            streams.FormSubmissionStream(self),
            streams.GoalStream(self),
            streams.LineItemStream(self),
            streams.MeetingStream(self),
            streams.NoteStream(self),
            streams.OwnersStream(self),
            streams.PostalMailStream(self),  # empty stream
            streams.PropertyStream(self),
            streams.QuoteStream(self),
            streams.TaskStream(self),
            streams.TicketPipelineStream(self),
            streams.UsersStream(self),
            streams.AnalyticsSourcesDaily(self),
            streams.AnalyticsPagesTotals(self),
            streams.AnalyticsPagesDaily(self),
            streams.AnalyticsSessionsDaily(self),
        ]


if __name__ == "__main__":
    TapHubspot.cli()
