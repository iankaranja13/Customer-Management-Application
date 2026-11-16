"""Tests for input validation and normalization rules."""

import pytest
from app.validators import (
    validate_name,
    validate_email,
    validate_phone,
    normalize_phone,
    validate_optional_text,
    validate_customer_data,
)


class TestNameValidation:
    """Tests for first_name and last_name validation."""

    @pytest.mark.parametrize(
        "name",
        [
            "Bo",  # Min length boundary (2)
            "Zoë",  # Unicode character
            "O'Brien",  # Apostrophe
            "Mary-Jane",  # Hyphen
            "Zoë O'Brien",  # Full name with space, unicode, and apostrophe
            "René François",  # Accented unicode characters
            "A" * 50,  # Max length boundary (50)
            "  John  ",  # Whitespace padding to be trimmed
        ],
    )
    def test_valid_names(self, name):
        ok, err, cleaned = validate_name(name, "First name")
        assert ok is True
        assert err == ""
        assert cleaned == name.strip()

    @pytest.mark.parametrize(
        "name,expected_err",
        [
            ("", "First name is required."),
            ("   ", "First name is required."),
            (None, "First name is required."),
            ("A", "First name must be at least 2 characters long."),
            ("A" * 51, "First name must not exceed 50 characters."),
            ("John123", "First name can only contain letters, spaces, hyphens, and apostrophes."),
            ("Mary@Jane", "First name can only contain letters, spaces, hyphens, and apostrophes."),
            ("<script>", "First name can only contain letters, spaces, hyphens, and apostrophes."),
            ("John_Doe", "First name can only contain letters, spaces, hyphens, and apostrophes."),
        ],
    )
    def test_invalid_names(self, name, expected_err):
        ok, err, _ = validate_name(name, "First name")
        assert ok is False
        assert expected_err in err


class TestEmailValidation:
    """Tests for email validation."""

    @pytest.mark.parametrize(
        "email,expected_clean",
        [
            ("user@example.com", "user@example.com"),
            ("USER@EXAMPLE.COM", "user@example.com"),
            ("  user@domain.co.uk  ", "user@domain.co.uk"),
            ("first.last+tag@sub.domain.org", "first.last+tag@sub.domain.org"),
        ],
    )
    def test_valid_emails(self, email, expected_clean):
        ok, err, cleaned = validate_email(email)
        assert ok is True
        assert err == ""
        assert cleaned == expected_clean

    @pytest.mark.parametrize(
        "email",
        [
            "",
            "   ",
            None,
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@com",
            "user..name@domain.com",
            "user@domain..com",
            "a" * 250 + "@test.com",  # Exceeds 254 chars
        ],
    )
    def test_invalid_emails(self, email):
        ok, err, _ = validate_email(email)
        assert ok is False
        assert len(err) > 0


class TestPhoneValidation:
    """Tests for phone normalization and validation."""

    @pytest.mark.parametrize(
        "raw,expected_norm",
        [
            ("1234567", "1234567"),  # 7 digits min boundary
            ("123456789012345", "123456789012345"),  # 15 digits max boundary
            ("+1 (555) 123-4567", "+15551234567"),
            ("+44 20 7946 0991", "+442079460991"),
            ("  +254 712 345 678  ", "+254712345678"),
            ("555.123.4567", "5551234567"),
            ("0712-345-678", "0712345678"),
        ],
    )
    def test_valid_phones(self, raw, expected_norm):
        ok, err, cleaned = validate_phone(raw)
        assert ok is True
        assert err == ""
        assert cleaned == expected_norm

    @pytest.mark.parametrize(
        "phone",
        [
            "",
            "   ",
            None,
            "123456",  # 6 digits (too short)
            "1234567890123456",  # 16 digits (too long)
            "+1-800-CALL-NOW",  # Contains letters
            "555-1234-abcd",
            "++1234567890",  # Multiple pluses
            "!@#$%^&*",
        ],
    )
    def test_invalid_phones(self, phone):
        ok, err, _ = validate_phone(phone)
        assert ok is False
        assert len(err) > 0


class TestOptionalFields:
    """Tests for address, city, country validation."""

    def test_optional_fields_empty(self):
        ok, err, cleaned = validate_optional_text("", "Address", 200)
        assert ok is True
        assert cleaned == ""

        ok, err, cleaned = validate_optional_text(None, "City", 60)
        assert ok is True
        assert cleaned == ""

    def test_optional_fields_within_limits(self):
        ok, err, cleaned = validate_optional_text("123 Main Street, Suite 4B", "Address", 200)
        assert ok is True
        assert cleaned == "123 Main Street, Suite 4B"

    def test_optional_fields_exceeding_limits(self):
        ok, err, _ = validate_optional_text("A" * 201, "Address", 200)
        assert ok is False
        assert "must not exceed 200" in err

        ok, err, _ = validate_optional_text("B" * 61, "City", 60)
        assert ok is False
        assert "must not exceed 60" in err


class TestValidateCustomerData:
    """Full form validation testing."""

    def test_complete_valid_form(self):
        data = {
            "first_name": " Zoë ",
            "last_name": " O'Brien ",
            "email": " Zoe.OBrien@Example.COM ",
            "phone": " +1 (555) 234-5678 ",
            "address": " 42 Wallaby Way ",
            "city": " Sydney ",
            "country": " Australia ",
        }
        is_valid, errors, cleaned = validate_customer_data(data)
        assert is_valid is True
        assert errors == {}
        assert cleaned["first_name"] == "Zoë"
        assert cleaned["last_name"] == "O'Brien"
        assert cleaned["email"] == "zoe.obrien@example.com"
        assert cleaned["phone"] == "+15552345678"
        assert cleaned["city"] == "Sydney"

    def test_multiple_invalid_fields(self):
        data = {
            "first_name": "J",  # too short
            "last_name": "D0e",  # contains number
            "email": "invalid-email",
            "phone": "123",  # too short
            "address": "A" * 205,  # too long
        }
        is_valid, errors, _ = validate_customer_data(data)
        assert is_valid is False
        assert "first_name" in errors
        assert "last_name" in errors
        assert "email" in errors
        assert "phone" in errors
        assert "address" in errors
