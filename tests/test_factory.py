from app import create_app


def test_config():
    """Test that app factory correctly applies test configuration."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_404_page(client):
    """Test that an unknown URL returns a custom 404 page."""
    response = client.get("/non-existent-page-xyz")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data
    assert b"404" in response.data
