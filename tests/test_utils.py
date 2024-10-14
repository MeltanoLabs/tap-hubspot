import pytest

from tap_hubspot.streams import convert_date_to_epoch


@pytest.mark.parametrize(
    "test_date, expected",
    [
        ("2024-07-01", 1719792000000),
        ("2024-07-01T12:00:00", 1719835200000),
        (1719792000000, 1719792000000),
    ],
)
def test_convert_date_to_epoch(test_date, expected):
    assert convert_date_to_epoch(test_date) == expected
