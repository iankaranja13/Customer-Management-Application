import os
import sqlite3
import click
from flask import current_app, g


def get_db():
    """Get or create database connection for the current application context."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database by executing schema.sql."""
    db = get_db()
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database teardown and CLI command with Flask application."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
