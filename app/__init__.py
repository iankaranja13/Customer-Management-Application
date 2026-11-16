import os
import secrets
from flask import Flask, redirect, url_for, session, request, abort, render_template


def create_app(test_config=None):
    """Application factory for Customer Management Application."""
    app = Flask(__name__, instance_relative_config=True)

    # Base configuration
    db_default_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "customers.db")
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-replace-in-production"),
        DATABASE=os.environ.get("DATABASE_PATH", db_default_path),
        CSRF_ENABLED=True,
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists if needed
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # CSRF Protection via session token
    def get_csrf_token():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_hex(16)
        return session["_csrf_token"]

    app.jinja_env.globals["csrf_token"] = get_csrf_token

    @app.before_request
    def check_csrf():
        if not app.config.get("CSRF_ENABLED", True):
            return
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
            expected = session.get("_csrf_token")
            if not token or not expected or token != expected:
                abort(400, description="CSRF token validation failed. Please try again.")

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html", error=error), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template("errors/400.html", error=error), 400

    # Root redirect
    @app.route("/")
    def index():
        return redirect(url_for("customers.list_customers"))

    # Register database teardown and CLI command
    from app import db
    db.init_app(app)

    # Register blueprint if routes module exists
    try:
        from app.routes import bp as customers_bp

        app.register_blueprint(customers_bp)
    except ImportError:
        pass

    return app
