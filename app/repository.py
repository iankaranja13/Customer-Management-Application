"""Repository module for Customer Management Application.

Provides data access methods for the customers table. All database queries
use parameterized SQL statements (? placeholders) to guarantee protection against
SQL injection attacks.
"""

from datetime import datetime
from app.db import get_db


def get_all_customers(sort_by="created_at", order="desc", limit=10, offset=0):
    """Retrieve paginated and sorted list of customers."""
    allowed_sort_fields = {
        "id": "id",
        "first_name": "first_name",
        "last_name": "last_name",
        "name": "last_name",
        "email": "email",
        "city": "city",
        "created_at": "created_at",
    }
    field = allowed_sort_fields.get(sort_by, "created_at")
    direction = "ASC" if order.lower() == "asc" else "DESC"

    db = get_db()
    query = f"""
        SELECT * FROM customers
        ORDER BY {field} {direction}
        LIMIT ? OFFSET ?
    """
    cursor = db.execute(query, (limit, offset))
    return cursor.fetchall()


def count_all_customers():
    """Count total number of customers."""
    db = get_db()
    cursor = db.execute("SELECT COUNT(*) AS count FROM customers")
    row = cursor.fetchone()
    return row["count"] if row else 0


def get_customer_by_id(customer_id):
    """Retrieve a single customer by primary key ID."""
    db = get_db()
    cursor = db.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    return cursor.fetchone()


def get_customer_by_email(email):
    """Retrieve a customer by email (case-insensitive)."""
    if not email:
        return None
    db = get_db()
    cursor = db.execute(
        "SELECT * FROM customers WHERE LOWER(email) = LOWER(?)", (email.strip(),)
    )
    return cursor.fetchone()


def create_customer(data):
    """Insert a new customer record."""
    db = get_db()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.execute(
        """
        INSERT INTO customers (
            first_name, last_name, email, phone, address, city, country, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["first_name"].strip(),
            data["last_name"].strip(),
            data["email"].strip().lower(),
            data["phone"].strip(),
            data.get("address", "").strip() or None,
            data.get("city", "").strip() or None,
            data.get("country", "").strip() or None,
            now,
            now,
        ),
    )
    db.commit()
    return cursor.lastrowid


def update_customer(customer_id, data):
    """Update an existing customer record."""
    db = get_db()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.execute(
        """
        UPDATE customers
        SET first_name = ?,
            last_name = ?,
            email = ?,
            phone = ?,
            address = ?,
            city = ?,
            country = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            data["first_name"].strip(),
            data["last_name"].strip(),
            data["email"].strip().lower(),
            data["phone"].strip(),
            data.get("address", "").strip() or None,
            data.get("city", "").strip() or None,
            data.get("country", "").strip() or None,
            now,
            customer_id,
        ),
    )
    db.commit()
    return cursor.rowcount > 0


def delete_customer(customer_id):
    """Delete a customer record by ID."""
    db = get_db()
    cursor = db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    db.commit()
    return cursor.rowcount > 0


def search_customers(query_text, sort_by="created_at", order="desc", limit=10, offset=0):
    """Search customers by partial match across all text fields (case-insensitive)."""
    if not query_text or not query_text.strip():
        return get_all_customers(sort_by, order, limit, offset)

    allowed_sort_fields = {
        "id": "id",
        "first_name": "first_name",
        "last_name": "last_name",
        "name": "last_name",
        "email": "email",
        "city": "city",
        "created_at": "created_at",
    }
    field = allowed_sort_fields.get(sort_by, "created_at")
    direction = "ASC" if order.lower() == "asc" else "DESC"

    term = f"%{query_text.strip()}%"
    db = get_db()
    sql = f"""
        SELECT * FROM customers
        WHERE first_name LIKE ?
           OR last_name LIKE ?
           OR email LIKE ?
           OR phone LIKE ?
           OR address LIKE ?
           OR city LIKE ?
           OR country LIKE ?
        ORDER BY {field} {direction}
        LIMIT ? OFFSET ?
    """
    cursor = db.execute(sql, (term, term, term, term, term, term, term, limit, offset))
    return cursor.fetchall()


def count_search_customers(query_text):
    """Count matches for search query."""
    if not query_text or not query_text.strip():
        return count_all_customers()

    term = f"%{query_text.strip()}%"
    db = get_db()
    sql = """
        SELECT COUNT(*) AS count FROM customers
        WHERE first_name LIKE ?
           OR last_name LIKE ?
           OR email LIKE ?
           OR phone LIKE ?
           OR address LIKE ?
           OR city LIKE ?
           OR country LIKE ?
    """
    cursor = db.execute(sql, (term, term, term, term, term, term, term))
    row = cursor.fetchone()
    return row["count"] if row else 0
