"""tap-hubspot tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_hubspot import streams
from tap_hubspot.client import AssociationsStream


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
            "custom_object_types",
            th.ArrayType(th.StringType),
            required=False,
            description=(
                "List of HubSpot custom CRM object type names to sync "
                "(e.g. ['patches']). Each name must match the API name or "
                "fullyQualifiedName in HubSpot. Requires a HubSpot Enterprise plan "
                "and the crm.objects.custom.read and crm.schemas.custom.read scopes."
            ),
        ),
        th.Property(
            "associations",
            th.ObjectType(additional_properties=th.ArrayType(th.StringType)),
            required=False,
            description=(
                "Mapping of from_object_type to a list of to_object_types to "
                "sync associations for, e.g. {'contact': ['company', "
                "'deal']}. Each from/to pair creates a stream named "
                "'<from_object_type>_<to_object_type>_associations'. Object "
                "type names must match HubSpot's object type names (e.g. "
                "'contact', 'company', 'deal', 'ticket'). No association "
                "streams are created unless this is set."
            ),
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.HubspotStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ContactStream(self),
            streams.UsersStream(self),
            streams.TeamsStream(self),
            streams.OwnersStream(self),
            streams.TicketPipelineStream(self),
            streams.DealPipelineStream(self),
            streams.EmailSubscriptionStream(self),
            streams.PropertyNotesStream(self),
            streams.CompanyStream(self),
            streams.DealStream(self),
            streams.LeadStream(self),
            streams.FeedbackSubmissionsStream(self),
            streams.LineItemStream(self),
            streams.ProductStream(self),
            streams.TicketStream(self),
            streams.QuoteStream(self),
            streams.GoalStream(self),
            streams.CallStream(self),
            streams.CommunicationStream(self),
            streams.EmailStream(self),
            streams.MeetingStream(self),
            streams.NoteStream(self),
            streams.PostalMailStream(self),
            streams.TaskStream(self),
            *[
                streams.CustomObjectStream(self, object_type)
                for object_type in self.config.get("custom_object_types", [])
            ],
            *[
                AssociationsStream(self, from_object_type, to_object_type)
                for from_object_type, to_object_types in self.config.get(
                    "associations",
                    {},
                ).items()
                for to_object_type in to_object_types
            ],
        ]


if __name__ == "__main__":
    TapHubspot.cli()
