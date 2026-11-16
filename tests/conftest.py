import os
import tempfile
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        from app.db import init_db
        init_db()

    yield app

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()
