"""Tests for search route integration and query filtering."""

from app import repository


def test_search_route_with_query(client, app):
    """GET /customers?q=... filters the customer table."""
    with app.app_context():
        repository.create_customer(
            {
                "first_name": "Sarah",
                "last_name": "Connor",
                "email": "sarah@cyberdyne.org",
                "phone": "+15551234567",
                "city": "Los Angeles",
            }
        )
        repository.create_customer(
            {
                "first_name": "John",
                "last_name": "Connor",
                "email": "john@resistance.net",
                "phone": "+15557654321",
                "city": "Santa Monica",
            }
        )
        repository.create_customer(
            {
                "first_name": "Kyle",
                "last_name": "Reese",
                "email": "kyle@future.net",
                "phone": "+15559871234",
                "city": "Los Angeles",
            }
        )

    # Search for "connor" (matches 2)
    response = client.get("/customers?q=connor")
    assert response.status_code == 200
    assert b"Sarah Connor" in response.data
    assert b"John Connor" in response.data
    assert b"Kyle Reese" not in response.data
    assert b"Found <strong>2</strong> matching customers" in response.data

    # Search for "los angeles" (matches 2: Sarah and Kyle)
    response = client.get("/customers?q=los+angeles")
    assert response.status_code == 200
    assert b"Sarah Connor" in response.data
    assert b"Kyle Reese" in response.data
    assert b"John Connor" not in response.data

    # Search for phone substring
    response = client.get("/customers?q=9871234")
    assert response.status_code == 200
    assert b"Kyle Reese" in response.data


def test_search_route_no_matches(client):
    """GET /customers?q=nomatch displays friendly no-results empty state."""
    response = client.get("/customers?q=NoSuchPersonExistsXYZ")
    assert response.status_code == 200
    assert b"No results found for" in response.data
    assert b"NoSuchPersonExistsXYZ" in response.data
    assert b"Clear Search Filter" in response.data


def test_search_empty_query_returns_all(client, app):
    """GET /customers?q= with blank query shows all customers."""
    with app.app_context():
        repository.create_customer(
            {
                "first_name": "Peter",
                "last_name": "Parker",
                "email": "peter@dailybugle.com",
                "phone": "+15553334444",
            }
        )

    response = client.get("/customers?q=   ")
    assert response.status_code == 200
    assert b"Peter Parker" in response.data
