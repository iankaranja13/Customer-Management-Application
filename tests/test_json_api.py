"""Tests for JSON responses used by dashboard modals and drawer.

HTML remains the default; JSON is served only when the client sends
``Accept: application/json``.
"""

from app import repository

JSON_HEADERS = {"Accept": "application/json"}


def _valid_customer():
    return {
        "first_name": "Wanjiku",
        "last_name": "Otieno",
        "email": "wanjiku@example.co.ke",
        "phone": "+254712345678",
        "city": "Nairobi",
    }


def test_json_create_success(client, app):
    """POST /customers/new with JSON Accept returns 201 payload."""
    response = client.post("/customers/new", data=_valid_customer(), headers=JSON_HEADERS)
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert "added successfully" in payload["message"]
    assert payload["customer"]["email"] == "wanjiku@example.co.ke"
    assert payload["stats"]["total"] == 1


def test_json_create_validation_errors(client):
    """Invalid JSON create returns 422 with field error mapping."""
    data = _valid_customer()
    data["email"] = "not-an-email"
    response = client.post("/customers/new", data=data, headers=JSON_HEADERS)
    assert response.status_code == 422
    payload = response.get_json()
    assert payload["success"] is False
    assert "email" in payload["errors"]
    assert "valid email address" in payload["errors"]["email"]


def test_json_view_customer(client, app):
    """GET /customers/<id> with JSON Accept returns the record."""
    with app.app_context():
        cid = repository.create_customer(_valid_customer())

    response = client.get(f"/customers/{cid}", headers=JSON_HEADERS)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["customer"]["first_name"] == "Wanjiku"
    assert payload["customer"]["phone"] == "+254712345678"


def test_json_view_not_found(client):
    """JSON detail for missing customer returns 404 payload."""
    response = client.get("/customers/99999", headers=JSON_HEADERS)
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_json_edit_success(client, app):
    """POST /customers/<id>/edit with JSON Accept returns updated record."""
    with app.app_context():
        cid = repository.create_customer(_valid_customer())

    data = _valid_customer()
    data["city"] = "Mombasa"
    response = client.post(f"/customers/{cid}/edit", data=data, headers=JSON_HEADERS)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "updated successfully" in payload["message"]
    assert payload["customer"]["city"] == "Mombasa"
    assert payload["customer"]["id"] == cid


def test_json_delete_success(client, app):
    """POST /customers/<id>/delete with JSON Accept returns stats."""
    with app.app_context():
        cid = repository.create_customer(_valid_customer())

    response = client.post(f"/customers/{cid}/delete", headers=JSON_HEADERS)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "successfully deleted" in payload["message"]
    assert payload["stats"]["total"] == 0

    with app.app_context():
        assert repository.get_customer_by_id(cid) is None


def test_json_delete_not_found(client):
    """JSON delete of missing customer returns 404 payload."""
    response = client.post("/customers/99999/delete", headers=JSON_HEADERS)
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_html_remains_default_without_json_accept(client, app):
    """Plain requests still receive HTML responses."""
    with app.app_context():
        cid = repository.create_customer(_valid_customer())

    response = client.get(f"/customers/{cid}")
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
