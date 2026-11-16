"""Route tests for customer registration and forms."""

from app import repository


def test_get_register_customer_form(client):
    """GET /customers/new should return 200 and display the form."""
    response = client.get("/customers/new")
    assert response.status_code == 200
    assert b"Register New Customer" in response.data
    assert b"first_name" in response.data
    assert b"last_name" in response.data
    assert b"email" in response.data
    assert b"phone" in response.data


def test_post_register_customer_success(client, app):
    """POST /customers/new with valid data should create record and redirect."""
    data = {
        "first_name": "Zoë",
        "last_name": "O'Brien",
        "email": "zoe.obrien@example.com",
        "phone": "+1 (555) 987-6543",
        "address": "42 Market Street",
        "city": "Boston",
        "country": "USA",
    }
    response = client.post("/customers/new", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"added successfully" in response.data
    assert b"Zo\xc3\xab O&#39;Brien" in response.data or b"Zo\xc3\xab O'Brien" in response.data

    with app.app_context():
        customer = repository.get_customer_by_email("zoe.obrien@example.com")
        assert customer is not None
        assert customer["first_name"] == "Zoë"
        assert customer["last_name"] == "O'Brien"
        assert customer["phone"] == "+15559876543"  # Normalized


def test_post_register_customer_validation_failure(client):
    """POST /customers/new with invalid data should return 422 and field errors."""
    data = {
        "first_name": "123",
        "last_name": "",
        "email": "not-an-email",
        "phone": "123",  # fewer than 7 digits
        "address": "Some address",
    }
    response = client.post("/customers/new", data=data)
    assert response.status_code == 422
    assert b"First name can only contain letters" in response.data
    assert b"Last name is required." in response.data
    assert b"Please enter a valid email address." in response.data
    assert b"Phone number must have at least 7 digits." in response.data
    # Preserves user input
    assert b"123" in response.data
    assert b"Some address" in response.data


def test_post_register_duplicate_email(client):
    """POST /customers/new should reject duplicate emails (case-insensitive)."""
    data1 = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone": "+15551234567",
    }
    res1 = client.post("/customers/new", data=data1, follow_redirects=True)
    assert res1.status_code == 200

    # Try inserting same email in uppercase
    data2 = {
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "ALICE@EXAMPLE.COM",
        "phone": "+15559876543",
    }
    res2 = client.post("/customers/new", data=data2)
    assert res2.status_code == 422
    assert "already registered" in response_text(res2)


def response_text(res):
    return res.data.decode("utf-8")
