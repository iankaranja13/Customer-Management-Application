"""Tests for customer update routes, pre-filled forms, and duplicate email logic."""

from app import repository


def test_get_edit_customer_form(client, app):
    """GET /customers/<id>/edit should pre-fill form with existing customer data."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Tony",
                "last_name": "Stark",
                "email": "tony@stark.com",
                "phone": "+15553000000",
                "address": "10880 Malibu Point",
                "city": "Malibu",
                "country": "USA",
            }
        )

    response = client.get(f"/customers/{cid}/edit")
    assert response.status_code == 200
    assert b"Edit Customer" in response.data
    assert b"Tony" in response.data
    assert b"Stark" in response.data
    assert b"tony@stark.com" in response.data
    assert b"+15553000000" in response.data
    assert b"10880 Malibu Point" in response.data


def test_get_edit_nonexistent_customer(client):
    """GET /customers/99999/edit returns 404."""
    response = client.get("/customers/99999/edit")
    assert response.status_code == 404


def test_post_edit_customer_success(client, app):
    """POST /customers/<id>/edit with valid data updates customer."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Bruce",
                "last_name": "Banner",
                "email": "bruce@avengers.org",
                "phone": "+15551239999",
                "city": "Dayton",
            }
        )

    data = {
        "first_name": "Bruce",
        "last_name": "Banner",
        "email": "hulk@avengers.org",  # Changed email
        "phone": "+1 (555) 999-8888",  # Changed phone
        "address": "Avengers Compound",
        "city": "Upstate NY",
        "country": "USA",
    }
    response = client.post(f"/customers/{cid}/edit", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated successfully" in response.data
    assert b"hulk@avengers.org" in response.data
    assert b"Upstate NY" in response.data

    with app.app_context():
        updated = repository.get_customer_by_id(cid)
        assert updated["email"] == "hulk@avengers.org"
        assert updated["phone"] == "+15559998888"
        assert updated["city"] == "Upstate NY"


def test_post_edit_keeping_same_email(client, app):
    """Updating a customer while keeping their existing email must NOT trigger duplicate error."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Steve",
                "last_name": "Rogers",
                "email": "steve@avengers.org",
                "phone": "+15551112233",
            }
        )

    data = {
        "first_name": "Steven",  # Changed first name
        "last_name": "Rogers",
        "email": "steve@avengers.org",  # Same email
        "phone": "+15551112233",
    }
    response = client.post(f"/customers/{cid}/edit", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated successfully" in response.data
    assert b"Steven Rogers" in response.data


def test_post_edit_conflicting_email(client, app):
    """Updating a customer to an email used by another customer must be rejected."""
    with app.app_context():
        repository.create_customer(
            {
                "first_name": "Natasha",
                "last_name": "Romanoff",
                "email": "natasha@shield.gov",
                "phone": "+15554443322",
            }
        )
        cid2 = repository.create_customer(
            {
                "first_name": "Clint",
                "last_name": "Barton",
                "email": "clint@shield.gov",
                "phone": "+15558887766",
            }
        )

    # Try setting Clint's email to Natasha's
    data = {
        "first_name": "Clint",
        "last_name": "Barton",
        "email": "NATASHA@SHIELD.GOV",  # Case-insensitive clash
        "phone": "+15558887766",
    }
    response = client.post(f"/customers/{cid2}/edit", data=data)
    assert response.status_code == 422
    assert b"already registered" in response.data


def test_post_edit_validation_errors(client, app):
    """Invalid data returns 422 and preserves submitted values."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Thor",
                "last_name": "Odinson",
                "email": "thor@asgard.gov",
                "phone": "+15559990000",
            }
        )

    data = {
        "first_name": "T",  # Too short
        "last_name": "123",  # Numbers not allowed
        "email": "not-an-email",
        "phone": "short",
    }
    response = client.post(f"/customers/{cid}/edit", data=data)
    assert response.status_code == 422
    assert b"First name must be at least 2 characters long." in response.data
    assert b"Last name can only contain letters" in response.data
