"""Routes module for Customer Management Application.

Encapsulates all customer-related endpoints inside a Flask Blueprint.
Handles request dispatching, validation orchestration, repository calls,
and template rendering.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from app import repository
from app.validators import validate_customer_data

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.route("", methods=["GET"])
def list_customers():
    """Display list of registered customers."""
    customers = repository.get_all_customers()
    return render_template("customers/list.html", customers=customers)


@bp.route("/new", methods=["GET", "POST"])
def create_customer():
    """Register a new customer."""
    if request.method == "POST":
        is_valid, errors, cleaned = validate_customer_data(request.form)

        # Check duplicate email (case-insensitive) if email syntax passed
        if "email" not in errors and cleaned.get("email"):
            existing = repository.get_customer_by_email(cleaned["email"])
            if existing:
                errors["email"] = "A customer with this email address is already registered."
                is_valid = False

        if not is_valid:
            flash("Please correct the errors in the form.", "danger")
            return (
                render_template(
                    "customers/form.html",
                    is_edit=False,
                    customer=request.form,
                    errors=errors,
                ),
                422,
            )

        customer_id = repository.create_customer(cleaned)
        flash(f"Customer {cleaned['first_name']} {cleaned['last_name']} added successfully.", "success")
        return redirect(url_for("customers.list_customers"))

    return render_template(
        "customers/form.html",
        is_edit=False,
        customer=None,
        errors={},
    )
