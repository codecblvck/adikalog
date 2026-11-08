import pytest

from app.auth.validators import validate_pin

MUST_PASS = [
    "2580", "4829", "0472", "1212", "1123", "1357", "1243", "1235",
    "7890", "8901", "9012", "0987", "1098", "2109",
]

MUST_FAIL = [
    "",
    "123",
    "12345",
    "12a4",
    "12 4",
    " 135",
    "135 ",
    "0000",
    "1111",
    "9999",
    "1234",
    "2345",
    "6789",
    "0123",
    "4321",
    "9876",
    "3210",
]

NONE_STRING = [1234, None]

@pytest.mark.parametrize("pin", MUST_PASS)
def test_valid_pins_are_accepted(pin):
    validate_pin(pin)


@pytest.mark.parametrize("pin", MUST_FAIL)
def test_invalid_pins_are_rejected(pin):
    with pytest.raises(ValueError):
        validate_pin(pin)

@pytest.mark.parametrize("pin", NONE_STRING)
def test_none_string_pin(pin):
    with pytest.raises(ValueError):
        validate_pin(pin)

def test_arabic_digit(pin="١٢٣٥"):
    with pytest.raises(ValueError):
        validate_pin(pin)
