"""Vercel serverless entrypoint for CustomerHub.

Exposes the Flask WSGI ``app`` and guarantees a usable SQLite database on
cold start: Vercel's filesystem is read-only except ``/tmp`` (ephemeral),
so the database is created there from a bundled template when present,
otherwise from ``schema.sql`` plus the demo seed data.
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from run import app  # noqa: E402


def _ensure_database(flask_app, template_path=None):
    """Create the serverless database on cold start if it is missing."""
    db_path = flask_app.config["DATABASE"]
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        return "existing"

    parent = os.path.dirname(db_path)
    if parent:
        try:
            os.makedirs(parent, exist_ok=True)
        except OSError:
            pass

    if template_path is None:
        template_path = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "customers.db")
        )
    try:
        if os.path.exists(template_path) and os.path.getsize(template_path) > 0:
            shutil.copyfile(template_path, db_path)
            return "template"
    except OSError:
        pass

    with flask_app.app_context():
        from app import db, repository
        from app.validators import validate_customer_data
        from seed import SAMPLE_CUSTOMERS

        db.init_db()
        for customer in SAMPLE_CUSTOMERS:
            is_valid, _errors, cleaned = validate_customer_data(customer)
            if is_valid:
                repository.create_customer(cleaned)
    return "seeded"


_ensure_database(app)
