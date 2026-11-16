"""Validation module for Customer Management Application.

Provides pure functions for input validation and normalization.
Server-side validation is the single source of truth for all customer records.
"""

import re
from typing import Dict, Tuple, Any

# Standard email regex pattern
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)


def validate_name(value: Any, field_name: str) -> Tuple[bool, str, str]:
    """Validate customer first or last name.

    Rules:
    - Required
    - 2-50 characters after trimming
    - Letters (including Unicode accents), spaces, hyphens, and apostrophes only.
    """
    if value is None:
        return False, f"{field_name} is required.", ""

    trimmed = str(value).strip()

    if not trimmed:
        return False, f"{field_name} is required.", ""

    if len(trimmed) < 2:
        return False, f"{field_name} must be at least 2 characters long.", trimmed

    if len(trimmed) > 50:
        return False, f"{field_name} must not exceed 50 characters.", trimmed

    for ch in trimmed:
        if not (ch.isalpha() or ch in (" ", "-", "'", "’")):
            return (
                False,
                f"{field_name} can only contain letters, spaces, hyphens, and apostrophes.",
                trimmed,
            )

    return True, "", trimmed


def validate_email(value: Any) -> Tuple[bool, str, str]:
    """Validate customer email address.

    Rules:
    - Required
    - Valid standard format
    - Max 254 characters
    - Returns lowercased trimmed email
    """
    if value is None:
        return False, "Email address is required.", ""

    trimmed = str(value).strip()

    if not trimmed:
        return False, "Email address is required.", ""

    if len(trimmed) > 254:
        return False, "Email address must not exceed 254 characters.", trimmed

    if not EMAIL_REGEX.match(trimmed) or ".." in trimmed:
        return False, "Please enter a valid email address.", trimmed

    return True, "", trimmed.lower()


def normalize_phone(value: Any) -> str:
    """Normalize phone number by keeping leading '+' and stripping formatting."""
    if not value:
        return ""
    trimmed = str(value).strip()
    has_plus = trimmed.startswith("+")
    digits = "".join(ch for ch in trimmed if ch.isdigit())
    return f"+{digits}" if has_plus else digits


def validate_phone(value: Any) -> Tuple[bool, str, str]:
    """Validate and normalize customer phone number.

    Rules:
    - Required
    - Allows spaces, dashes, parentheses, dots, and optional leading '+' in input
    - Must contain between 7 and 15 digits
    - Returns normalized phone string
    """
    if value is None:
        return False, "Phone number is required.", ""

    raw = str(value).strip()
    if not raw:
        return False, "Phone number is required.", ""

    # Check for invalid characters (only digits, spaces, dashes, dots, parentheses, leading plus)
    allowed_chars = set("0123456789 -().")
    check_chars = raw[1:] if raw.startswith("+") else raw
    if any(ch not in allowed_chars for ch in check_chars):
        return (
            False,
            "Phone number contains invalid characters. Only digits, spaces, dashes, and parentheses are allowed.",
            raw,
        )

    normalized = normalize_phone(raw)
    digit_count = sum(1 for ch in normalized if ch.isdigit())

    if digit_count < 7:
        return False, "Phone number must have at least 7 digits.", raw

    if digit_count > 15:
        return False, "Phone number must not exceed 15 digits.", raw

    return True, "", normalized


def validate_optional_text(
    value: Any, field_name: str, max_length: int
) -> Tuple[bool, str, str]:
    """Validate optional text fields such as address, city, country."""
    if value is None:
        return True, "", ""

    trimmed = str(value).strip()
    if not trimmed:
        return True, "", ""

    if len(trimmed) > max_length:
        return False, f"{field_name} must not exceed {max_length} characters.", trimmed

    return True, "", trimmed


def validate_customer_data(
    data: Dict[str, Any]
) -> Tuple[bool, Dict[str, str], Dict[str, Any]]:
    """Validate complete customer form data.

    Returns:
    - is_valid: True if all fields passed validation
    - errors: dictionary mapping field names to error messages
    - cleaned_data: dictionary with normalized, trimmed values
    """
    errors: Dict[str, str] = {}
    cleaned: Dict[str, Any] = {}

    # First Name
    ok, err, val = validate_name(data.get("first_name"), "First name")
    if not ok:
        errors["first_name"] = err
    cleaned["first_name"] = val

    # Last Name
    ok, err, val = validate_name(data.get("last_name"), "Last name")
    if not ok:
        errors["last_name"] = err
    cleaned["last_name"] = val

    # Email
    ok, err, val = validate_email(data.get("email"))
    if not ok:
        errors["email"] = err
    cleaned["email"] = val

    # Phone
    ok, err, val = validate_phone(data.get("phone"))
    if not ok:
        errors["phone"] = err
    cleaned["phone"] = val

    # Address (optional, max 200)
    ok, err, val = validate_optional_text(data.get("address"), "Address", 200)
    if not ok:
        errors["address"] = err
    cleaned["address"] = val

    # City (optional, max 60)
    ok, err, val = validate_optional_text(data.get("city"), "City", 60)
    if not ok:
        errors["city"] = err
    cleaned["city"] = val

    # Country (optional, max 60)
    ok, err, val = validate_optional_text(data.get("country"), "Country", 60)
    if not ok:
        errors["country"] = err
    cleaned["country"] = val

    return (len(errors) == 0, errors, cleaned)
