"""Tests standard tap features using the built-in SDK tests library."""

import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_hubspot.tap import TapHubspot

SAMPLE_CONFIG = {
    "start_date": "2020-01-01",
    "client_id": os.getenv("TAP_HUBSPOT_CLIENT_ID"),
    "client_secret": os.getenv("TAP_HUBSPOT_CLIENT_SECRET"),
    "refresh_token": os.getenv("TAP_HUBSPOT_REFRESH_TOKEN"),
    "access_token": os.getenv("TAP_HUBSPOT_ACCESS_TOKEN"),
}


TestTapHubspot = get_tap_test_class(
    tap_class=TapHubspot,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        max_records_limit=10,
        ignore_no_records_for_streams=["postal_mail", "forms"],
    ),
)
