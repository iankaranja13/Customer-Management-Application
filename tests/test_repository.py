"""Tests for repository data access methods, queries, and search."""

from app import repository


def test_repository_create_and_get_by_id(app):
    """Test inserting a customer and retrieving by ID."""
    with app.app_context():
        data = {
            "first_name": "Marcus",
            "last_name": "Brody",
            "email": "marcus@museum.org",
            "phone": "+15551239876",
            "address": "12 University Way",
            "city": "Barnett",
            "country": "USA",
        }
        cid = repository.create_customer(data)
        assert cid is not None
        assert cid > 0

        customer = repository.get_customer_by_id(cid)
        assert customer is not None
        assert customer["first_name"] == "Marcus"
        assert customer["last_name"] == "Brody"
        assert customer["email"] == "marcus@museum.org"
        assert customer["phone"] == "+15551239876"
        assert customer["city"] == "Barnett"


def test_repository_get_by_email_case_insensitive(app):
    """Test get_customer_by_email handles mixed casing."""
    with app.app_context():
        data = {
            "first_name": "Marion",
            "last_name": "Ravenwood",
            "email": "marion@nepal.org",
            "phone": "+15557774433",
        }
        repository.create_customer(data)

        # Lookup with uppercase
        found = repository.get_customer_by_email("MARION@NEPAL.ORG")
        assert found is not None
        assert found["first_name"] == "Marion"

        # Non-existent
        assert repository.get_customer_by_email("notfound@example.com") is None


def test_repository_search_partial_and_case_insensitive(app):
    """Test search matches partially across multiple fields case-insensitively."""
    with app.app_context():
        repository.create_customer(
            {
                "first_name": "Indiana",
                "last_name": "Jones",
                "email": "indy@marshall.edu",
                "phone": "+15550001936",
                "city": "Princeton",
                "country": "United States",
            }
        )
        repository.create_customer(
            {
                "first_name": "Henry",
                "last_name": "Jones",
                "email": "henry.sr@grail.org",
                "phone": "+15550001989",
                "city": "Venice",
                "country": "Italy",
            }
        )

        # Search by partial first name lower case
        results = repository.search_customers("indiana")
        assert len(results) == 1
        assert results[0]["first_name"] == "Indiana"

        # Search by shared last name
        results = repository.search_customers("jones")
        assert len(results) == 2

        # Search by full concatenated name
        results = repository.search_customers("Henry Jones")
        assert len(results) == 1
        assert results[0]["email"] == "henry.sr@grail.org"

        # Search by email fragment
        results = repository.search_customers("marshall.edu")
        assert len(results) == 1

        # Search by city
        results = repository.search_customers("venice")
        assert len(results) == 1

        # Search with no results
        results = repository.search_customers("NonExistentTermXYZ")
        assert len(results) == 0
        assert repository.count_search_customers("NonExistentTermXYZ") == 0


def test_repository_delete(app):
    """Test deleting a customer record."""
    with app.app_context():
        cid = repository.create_customer(
            {
                "first_name": "To",
                "last_name": "Delete",
                "email": "delete.me@example.com",
                "phone": "+15559998888",
            }
        )
        assert repository.get_customer_by_id(cid) is not None

        deleted = repository.delete_customer(cid)
        assert deleted is True
        assert repository.get_customer_by_id(cid) is None

        # Deleting non-existent ID
        assert repository.delete_customer(99999) is False
