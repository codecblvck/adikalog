import pytest

from app.auth.validators import NAME_MAX_LENGTH, validate_name


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("ada", "ada"),
        ("Ada", "ada"),
        ("ADA", "ada"),
        ("  ada  ", "ada"),
        ("\tada\n", "ada"),
        ("Ada Obi", "ada obi"),
    ],
)
def test_valid_names_are_cleaned(raw, expected):
    assert validate_name(raw) == expected


@pytest.mark.parametrize("raw", ["", " ", "   ", "\t\n"])
def test_empty_or_whitespace_name_rejected(raw):
    with pytest.raises(ValueError, match="empty"):
        validate_name(raw)


def test_name_at_max_length_is_accepted():
    name = "a" * NAME_MAX_LENGTH
    assert validate_name(name) == name


def test_name_over_max_length_is_rejected():
    with pytest.raises(ValueError, match="longer"):
        validate_name("a" * (NAME_MAX_LENGTH + 1))


def test_padded_name_at_max_length_is_accepted():
    name = "a" * NAME_MAX_LENGTH
    assert validate_name(f"  {name}  ") == name


@pytest.mark.parametrize("raw", [None, 123, b"ada", ["ada"]])
def test_non_string_rejected(raw):
    with pytest.raises(ValueError, match="text"):
        validate_name(raw)
