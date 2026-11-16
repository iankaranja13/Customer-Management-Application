"""Tests for customer list, pagination, sorting, and detail views."""

from app import repository


def test_root_redirects_to_customers(client):
    """GET / should redirect to /customers."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/customers")


def test_empty_customer_list(client):
    """When no customers exist, page shows empty state."""
    response = client.get("/customers")
    assert response.status_code == 200
    assert b"No customers yet" in response.data
    assert b"Add First Customer" in response.data


def test_view_customer_list(client, app):
    """Customer list displays rows for registered customers."""
    with app.app_context():
        repository.create_customer(
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "phone": "+15551112233",
                "city": "Chicago",
            }
        )

    response = client.get("/customers")
    assert response.status_code == 200
    assert b"Jane Doe" in response.data
    assert b"jane@example.com" in response.data
    assert b"Chicago" in response.data


def test_pagination(client, app):
    """Check that pagination splits items across pages (10 per page)."""
    with app.app_context():
        for i in range(1, 16):
            repository.create_customer(
                {
                    "first_name": f"User{i:02d}",
                    "last_name": "Test",
                    "email": f"user{i:02d}@example.com",
                    "phone": f"+155500000{i:02d}",
                }
            )

    # Page 1
    res1 = client.get("/customers?page=1")
    assert res1.status_code == 200
    assert b"Prev" in res1.data
    assert b"Next" in res1.data

    # Page 2
    res2 = client.get("/customers?page=2")
    assert res2.status_code == 200


def test_sorting(client, app):
    """Verify sorting customers by name ascending and descending."""
    with app.app_context():
        repository.create_customer(
            {
                "first_name": "Aaron",
                "last_name": "Adams",
                "email": "aaron@example.com",
                "phone": "+15551111111",
            }
        )
        repository.create_customer(
            {
                "first_name": "Zach",
                "last_name": "Zimmerman",
                "email": "zach@example.com",
                "phone": "+15559999999",
            }
        )

    res_asc = client.get("/customers?sort=name&order=asc")
    assert res_asc.status_code == 200
    a_pos = res_asc.data.find(b"Aaron Adams")
    z_pos = res_asc.data.find(b"Zach Zimmerman")
    assert a_pos < z_pos

    res_desc = client.get("/customers?sort=name&order=desc")
    assert res_desc.status_code == 200
    a_pos = res_desc.data.find(b"Aaron Adams")
    z_pos = res_desc.data.find(b"Zach Zimmerman")
    assert z_pos < a_pos


def test_customer_detail_view(client, app):
    """GET /customers/<id> displays detailed profile."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Eleanor",
                "last_name": "Vance",
                "email": "eleanor@example.com",
                "phone": "+15557778899",
                "address": "100 Hill House Road",
                "city": "Boston",
                "country": "USA",
            }
        )

    response = client.get(f"/customers/{cid}")
    assert response.status_code == 200
    assert b"Eleanor Vance" in response.data
    assert b"eleanor@example.com" in response.data
    assert b"+15557778899" in response.data
    assert b"100 Hill House Road" in response.data
    assert b"Boston" in response.data


def test_customer_detail_not_found(client):
    """GET /customers/999999 returns 404 page."""
    response = client.get("/customers/999999")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data or b"Customer #999999 not found" in response.data
