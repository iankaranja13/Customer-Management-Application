"""Routes module for Customer Management Application.

Encapsulates all customer-related endpoints inside a Flask Blueprint.
Handles request dispatching, validation orchestration, repository calls,
pagination, sorting, search, and template rendering.

POST/GET endpoints serve HTML by default and JSON when the client sends
``Accept: application/json`` (used by the dashboard modals and drawer).
"""

import math
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from app import repository
from app.validators import validate_customer_data

bp = Blueprint("customers", __name__, url_prefix="/customers")

PER_PAGE_OPTIONS = (10, 25, 50)
DEFAULT_PER_PAGE = 10
RECENT_DAYS = 30


def wants_json():
    """Return True when the client explicitly asks for a JSON response."""
    return "application/json" in request.headers.get("Accept", "")


def customer_to_dict(customer):
    """Serialize a customer row to a plain dict."""
    return {key: customer[key] for key in customer.keys()}


def dashboard_stats():
    """Return live dashboard metrics derived from database records."""
    return {
        "total": repository.count_all_customers(),
        "recent": repository.count_recent_customers(RECENT_DAYS),
        "recent_days": RECENT_DAYS,
        "cities": repository.count_distinct_cities(),
    }


@bp.route("", methods=["GET"])
def list_customers():
    """Display paginated, sortable, and searchable list of customers."""
    page = request.args.get("page", 1, type=int)
    if not page or page < 1:
        page = 1

    per_page = request.args.get("per_page", DEFAULT_PER_PAGE, type=int)
    if per_page not in PER_PAGE_OPTIONS:
        per_page = DEFAULT_PER_PAGE

    query = request.args.get("q", "").strip()
    sort_by = request.args.get("sort", "created_at").strip()
    order = request.args.get("order", "desc").strip().lower()
    if order not in ("asc", "desc"):
        order = "desc"

    if query:
        total = repository.count_search_customers(query)
        total_pages = max(1, math.ceil(total / per_page))
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page
        customers = repository.search_customers(
            query_text=query,
            sort_by=sort_by,
            order=order,
            limit=per_page,
            offset=offset,
        )
    else:
        total = repository.count_all_customers()
        total_pages = max(1, math.ceil(total / per_page))
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page
        customers = repository.get_all_customers(
            sort_by=sort_by,
            order=order,
            limit=per_page,
            offset=offset,
        )

    return render_template(
        "customers/list.html",
        customers=customers,
        page=page,
        total_pages=total_pages,
        total=total,
        query=query,
        sort_by=sort_by,
        order=order,
        per_page=per_page,
        per_page_options=PER_PAGE_OPTIONS,
        stats=dashboard_stats(),
    )


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
            if wants_json():
                return (
                    jsonify(
                        success=False,
                        message="Please correct the errors in the form.",
                        errors=errors,
                    ),
                    422,
                )
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
        message = (
            f"Customer {cleaned['first_name']} {cleaned['last_name']} added successfully."
        )
        if wants_json():
            customer = repository.get_customer_by_id(customer_id)
            return (
                jsonify(
                    success=True,
                    message=message,
                    customer=customer_to_dict(customer),
                    stats=dashboard_stats(),
                ),
                201,
            )
        flash(message, "success")
        return redirect(url_for("customers.list_customers"))

    return render_template(
        "customers/form.html",
        is_edit=False,
        customer=None,
        errors={},
    )


@bp.route("/<int:id>", methods=["GET"])
def view_customer(id):
    """Display detailed profile of a single customer."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        if wants_json():
            return (
                jsonify(
                    success=False, message=f"Customer #{id} not found."
                ),
                404,
            )
        abort(404, description=f"Customer #{id} not found.")
    if wants_json():
        return jsonify(success=True, customer=customer_to_dict(customer))
    return render_template("customers/detail.html", customer=customer)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_customer(id):
    """Edit an existing customer profile."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        if wants_json():
            return (
                jsonify(
                    success=False, message=f"Customer #{id} not found."
                ),
                404,
            )
        abort(404, description=f"Customer #{id} not found.")

    if request.method == "POST":
        is_valid, errors, cleaned = validate_customer_data(request.form)

        # Check duplicate email ignoring current customer ID
        if "email" not in errors and cleaned.get("email"):
            existing = repository.get_customer_by_email(cleaned["email"])
            if existing and existing["id"] != id:
                errors["email"] = "A customer with this email address is already registered."
                is_valid = False

        if not is_valid:
            if wants_json():
                return (
                    jsonify(
                        success=False,
                        message="Please correct the errors in the form.",
                        errors=errors,
                    ),
                    422,
                )
            flash("Please correct the errors in the form.", "danger")
            form_data = dict(request.form)
            form_data["id"] = id
            return (
                render_template(
                    "customers/form.html",
                    is_edit=True,
                    customer=form_data,
                    errors=errors,
                ),
                422,
            )

        repository.update_customer(id, cleaned)
        message = (
            f"Customer {cleaned['first_name']} {cleaned['last_name']} updated successfully."
        )
        if wants_json():
            updated = repository.get_customer_by_id(id)
            return jsonify(
                success=True,
                message=message,
                customer=customer_to_dict(updated),
                stats=dashboard_stats(),
            )
        flash(message, "success")
        return redirect(url_for("customers.view_customer", id=id))

    return render_template(
        "customers/form.html",
        is_edit=True,
        customer=customer,
        errors={},
    )


@bp.route("/<int:id>/delete/confirm", methods=["GET"])
def confirm_delete_customer(id):
    """Render confirmation page prior to customer deletion."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        abort(404, description=f"Customer #{id} not found.")
    return render_template("customers/confirm_delete.html", customer=customer)


@bp.route("/<int:id>/delete", methods=["POST"])
def delete_customer(id):
    """Delete a customer record (POST-only with confirmation)."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        if wants_json():
            return (
                jsonify(
                    success=False, message=f"Customer #{id} not found."
                ),
                404,
            )
        abort(404, description=f"Customer #{id} not found.")

    first_name = customer["first_name"]
    last_name = customer["last_name"]
    repository.delete_customer(id)
    message = f"Customer {first_name} {last_name} was successfully deleted."
    if wants_json():
        return jsonify(success=True, message=message, stats=dashboard_stats())
    flash(message, "success")
    return redirect(url_for("customers.list_customers"))
