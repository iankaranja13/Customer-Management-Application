"""Routes module for Customer Management Application.

Encapsulates all customer-related endpoints inside a Flask Blueprint.
Handles request dispatching, validation orchestration, repository calls,
pagination, sorting, search, and template rendering.
"""

import math
from flask import (
    Blueprint,
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


@bp.route("", methods=["GET"])
def list_customers():
    """Display paginated, sortable, and searchable list of customers."""
    page = request.args.get("page", 1, type=int)
    if not page or page < 1:
        page = 1

    per_page = 10
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


@bp.route("/<int:id>", methods=["GET"])
def view_customer(id):
    """Display detailed profile of a single customer."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        abort(404, description=f"Customer #{id} not found.")
    return render_template("customers/detail.html", customer=customer)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_customer(id):
    """Placeholder for edit route, expanded in feature/update-customer."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        abort(404, description=f"Customer #{id} not found.")
    return render_template("customers/form.html", is_edit=True, customer=customer, errors={})


@bp.route("/<int:id>/delete/confirm", methods=["GET"])
def confirm_delete_customer(id):
    """Placeholder for delete confirmation, expanded in feature/delete-customer."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        abort(404, description=f"Customer #{id} not found.")
    return redirect(url_for("customers.view_customer", id=id))


@bp.route("/<int:id>/delete", methods=["POST"])
def delete_customer(id):
    """Placeholder for delete route, expanded in feature/delete-customer."""
    customer = repository.get_customer_by_id(id)
    if customer is None:
        abort(404, description=f"Customer #{id} not found.")
    return redirect(url_for("customers.list_customers"))
