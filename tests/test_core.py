"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_hubspot.tap import TapHubspot

SAMPLE_CONFIG = {
    "start_date": "2023-01-01T00:00:00Z",
}


TestTapHubspot = get_tap_test_class(
    TapHubspot,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(),
)
