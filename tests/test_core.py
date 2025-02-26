"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_hubspot.tap import TapHubspot

SAMPLE_CONFIG = {
    "start_date": "2023-10-01T00:00:00.0Z",
}


TestTapHubspot = get_tap_test_class(
    tap_class=TapHubspot,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        max_records_limit=10,
        ignore_no_records_for_streams=[
            "calls",
            "communications",
            "emails",
            "feedback_submissions",
            "goal_targets",
            "line_items",
            "meetings",
            "notes",
            "postal_mail",
            "products",
            "quotes",
        ],
    ),
)
