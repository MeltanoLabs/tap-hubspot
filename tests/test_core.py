"""Tests standard tap features using the built-in SDK tests library."""

import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class
from tap_hubspot.tap import TapHubspot

SAMPLE_CONFIG = {
    "start_date": "2023-10-01T00:00:00.0Z",
    "client_id": os.environ["TAP_HUBSPOT_CLIENT_ID"],
    "client_secret":  os.environ["TAP_HUBSPOT_CLIENT_SECRET"],
    "refresh_token":  os.environ["TAP_HUBSPOT_REFRESH_TOKEN"],
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
            "meetings",
            "notes",
            "postal_mail",
        ]
    ),
)
