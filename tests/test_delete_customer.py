"""Tests for customer deletion, confirmation flow, and POST-only enforcement."""

from app import repository


def test_get_confirm_delete_page(client, app):
    """GET /customers/<id>/delete/confirm renders confirmation page."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Wanda",
                "last_name": "Maximoff",
                "email": "wanda@westview.org",
                "phone": "+15558881234",
                "city": "Westview",
            }
        )

    response = client.get(f"/customers/{cid}/delete/confirm")
    assert response.status_code == 200
    assert b"Confirm Customer Deletion" in response.data
    assert b"Wanda Maximoff" in response.data
    assert b"wanda@westview.org" in response.data
    assert b"Yes, Delete Customer" in response.data


def test_get_confirm_delete_not_found(client):
    """GET confirmation for non-existent customer returns 404."""
    response = client.get("/customers/99999/delete/confirm")
    assert response.status_code == 404


def test_post_delete_customer_success(client, app):
    """POST /customers/<id>/delete removes record and redirects."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Vision",
                "last_name": "Synthezoid",
                "email": "vision@avengers.org",
                "phone": "+15550009999",
            }
        )

    response = client.post(f"/customers/{cid}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"successfully deleted" in response.data

    with app.app_context():
        assert repository.get_customer_by_id(cid) is None


def test_delete_requires_post_method(client, app):
    """GET /customers/<id>/delete is rejected with 405 Method Not Allowed."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "Peter",
                "last_name": "Quill",
                "email": "starlord@guardians.org",
                "phone": "+15557770000",
            }
        )

    response = client.get(f"/customers/{cid}/delete")
    assert response.status_code == 405

    # Record must still exist in DB
    with app.app_context():
        assert repository.get_customer_by_id(cid) is not None


def test_post_delete_nonexistent_customer(client):
    """POST /customers/99999/delete returns 404."""
    response = client.post("/customers/99999/delete")
    assert response.status_code == 404


def test_delete_compacts_customer_ids(client, app):
    """Deleting a customer shifts higher IDs down to fill the gap."""
    with app.app_context():
        ids = [
            repository.create_customer(
                {
                    "first_name": "Test",
                    "last_name": f"User{n}",
                    "email": f"compact-user{n}@example.com",
                    "phone": f"+1555000000{n}",
                }
            )
            for n in range(1, 4)
        ]
    assert ids == [1, 2, 3]

    response = client.post("/customers/2/delete", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        # Former ID 3 now occupies ID 2; no record holds ID 3.
        shifted = repository.get_customer_by_id(2)
        assert shifted is not None
        assert shifted["email"] == "compact-user3@example.com"
        assert repository.get_customer_by_id(3) is None

        # Next insert continues the compact sequence with no trailing gap.
        new_id = repository.create_customer(
            {
                "first_name": "Test",
                "last_name": "UserNew",
                "email": "compact-user-new@example.com",
                "phone": "+15550000009",
            }
        )
        assert new_id == 3
