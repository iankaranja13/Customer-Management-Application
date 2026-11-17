"""Tests for dashboard statistics and page-size selection."""

from app import repository
from app.db import get_db


def _make_customer(n, city="Nairobi"):
    return {
        "first_name": "Test",
        "last_name": f"User{n}",
        "email": f"dash-user{n}@example.com",
        "phone": f"+2547000000{n:02d}",
        "city": city,
    }


def test_dashboard_stats_rendered(client, app):
    """List page shows live total, recent, and city metrics."""
    with app.app_context():
        repository.create_customer(_make_customer(1, city="Nairobi"))
        repository.create_customer(_make_customer(2, city="Mombasa"))
        repository.create_customer(_make_customer(3, city="nairobi"))

    response = client.get("/customers")
    assert response.status_code == 200
    assert b'data-stat="total">3<' in response.data
    assert b'data-stat="recent">3<' in response.data
    # Nairobi counted once despite case difference
    assert b'data-stat="cities">2<' in response.data
    assert b"Last 30 days" in response.data


def test_recent_stat_excludes_old_records(client, app):
    """Customers registered over 30 days ago are excluded from recent count."""
    with app.app_context():
        repository.create_customer(_make_customer(1))
        db = get_db()
        db.execute(
            "UPDATE customers SET created_at = datetime('now', '-60 days')"
            " WHERE email = ?",
            ("dash-user1@example.com",),
        )
        db.commit()
        assert repository.count_recent_customers(30) == 0
        assert repository.count_all_customers() == 1

    response = client.get("/customers")
    assert b'data-stat="total">1<' in response.data
    assert b'data-stat="recent">0<' in response.data


def test_cities_stat_ignores_blank(client, app):
    """Blank or missing cities are excluded from the cities metric."""
    with app.app_context():
        repository.create_customer(_make_customer(1, city="Kisumu"))
        repository.create_customer(_make_customer(2, city="   "))
        data = _make_customer(3)
        del data["city"]
        repository.create_customer(data)
        assert repository.count_distinct_cities() == 1


def test_per_page_selection(client, app):
    """per_page=25 shows all 12 records on a single page."""
    with app.app_context():
        for i in range(1, 13):
            repository.create_customer(_make_customer(i))

    response = client.get("/customers?per_page=25")
    assert response.status_code == 200
    assert b"dash-user1@example.com" in response.data
    assert b"dash-user12@example.com" in response.data
    assert b"Prev" not in response.data
    assert b"Next" not in response.data


def test_per_page_invalid_falls_back_to_default(client, app):
    """Unsupported per_page values fall back to 10 per page."""
    with app.app_context():
        for i in range(1, 13):
            repository.create_customer(_make_customer(i))

    response = client.get("/customers?per_page=7")
    assert response.status_code == 200
    assert b"dash-user12@example.com" not in response.data
    assert b"Prev" in response.data
    assert b"Next" in response.data
