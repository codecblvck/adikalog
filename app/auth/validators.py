import re

PIN_LENGTH = 4
ASCENDING_PIN = "0123456789"
DESCENDING_PIN = "9876543210"
NAME_MAX_LENGTH = 64


def validate_name(name):
    if not isinstance(name, str):
        raise ValueError("Name must be text.")

    cleaned = name.strip().lower()

    if not cleaned:
        raise ValueError("Name cannot be empty.")
    if len(cleaned) > NAME_MAX_LENGTH:
        raise ValueError(f"Name cannot be longer than {NAME_MAX_LENGTH} characters.")

    return cleaned


def validate_pin(pin):
    if not isinstance(pin, str):
        raise ValueError("PIN must be a string")
    if not re.fullmatch(rf"[0-9]{{{PIN_LENGTH}}}", pin):
        raise ValueError(f"PIN must be exactly {PIN_LENGTH} digits")
    if len(set(pin)) == 1:
        raise ValueError("PIN cannot be all the same digit")
    if pin in ASCENDING_PIN or pin in DESCENDING_PIN:
        raise ValueError("PIN cannot be a straight run")
