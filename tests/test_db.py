import sqlite3
import pytest
from app.db import get_db, close_db


def test_get_close_db(app):
    """Test that get_db returns the same connection and close_db closes it."""
    with app.app_context():
        db = get_db()
        assert db is get_db()
        assert isinstance(db, sqlite3.Connection)

    # Context is closed, attempting query on closed connection raises ProgrammingError
    with pytest.raises(sqlite3.ProgrammingError) as exc_info:
        db.execute("SELECT 1")
    assert "closed" in str(exc_info.value).lower()


def test_init_db_command(runner, monkeypatch):
    """Test the init-db CLI command calls init_db and outputs confirmation."""
    recorded = []

    def mock_init_db():
        recorded.append(True)

    monkeypatch.setattr("app.db.init_db", mock_init_db)
    result = runner.invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Initialized the database." in result.output
    assert len(recorded) == 1


def test_table_exists(app):
    """Test that the customers table exists and has expected columns."""
    with app.app_context():
        db = get_db()
        cursor = db.execute("PRAGMA table_info(customers)")
        columns = {row["name"] for row in cursor.fetchall()}
        expected = {
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "created_at",
            "updated_at",
        }
        assert expected.issubset(columns)
