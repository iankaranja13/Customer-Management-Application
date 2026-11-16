#!/usr/bin/env python3
"""Database Seeder Script for CustomerHub.

Seeds the SQLite database with 15 realistic customer profiles for demos,
manual exploratory testing, and evaluations.
"""

import sys
from app import create_app, db, repository

SAMPLE_CUSTOMERS = [
    {
        "first_name": "Zoë",
        "last_name": "O'Brien",
        "email": "zoe.obrien@apextech.com",
        "phone": "+1 (555) 234-5678",
        "address": "742 Evergreen Terrace",
        "city": "Springfield",
        "country": "United States",
    },
    {
        "first_name": "Marcus",
        "last_name": "Vance",
        "email": "m.vance@vancecorp.co.uk",
        "phone": "+44 20 7946 0912",
        "address": "10 Downing Place, Suite 4",
        "city": "London",
        "country": "United Kingdom",
    },
    {
        "first_name": "Amara",
        "last_name": "Kowalski",
        "email": "amara.k@nordicventures.de",
        "phone": "+49 30 12345678",
        "address": "Friedrichstraße 44",
        "city": "Berlin",
        "country": "Germany",
    },
    {
        "first_name": "René",
        "last_name": "François",
        "email": "rene.francois@lumierestudio.fr",
        "phone": "+33 1 42 68 55 00",
        "address": "15 Rue de la Paix",
        "city": "Paris",
        "country": "France",
    },
    {
        "first_name": "Elena",
        "last_name": "Rostova",
        "email": "elena.rostova@auroraglobal.ca",
        "phone": "+1 416 555 0199",
        "address": "250 University Avenue",
        "city": "Toronto",
        "country": "Canada",
    },
    {
        "first_name": "Kenji",
        "last_name": "Sato",
        "email": "kenji.sato@zenithpacific.jp",
        "phone": "+81 3 5555 0142",
        "address": "1-1-2 Otemachi, Chiyoda-ku",
        "city": "Tokyo",
        "country": "Japan",
    },
    {
        "first_name": "Fatima",
        "last_name": "Al-Zahra",
        "email": "fatima.alzahra@crescentholdings.ae",
        "phone": "+971 4 312 8900",
        "address": "Sheikh Zayed Road, Tower 1",
        "city": "Dubai",
        "country": "United Arab Emirates",
    },
    {
        "first_name": "Carlos",
        "last_name": "Mendoza",
        "email": "carlos.mendoza@solarsolutions.mx",
        "phone": "+52 55 5555 1234",
        "address": "Paseo de la Reforma 222",
        "city": "Mexico City",
        "country": "Mexico",
    },
    {
        "first_name": "Priya",
        "last_name": "Sharma",
        "email": "priya.sharma@innovateindia.in",
        "phone": "+91 80 2345 6789",
        "address": "100 Outer Ring Road",
        "city": "Bengaluru",
        "country": "India",
    },
    {
        "first_name": "Liam",
        "last_name": "O'Connor",
        "email": "liam.oconnor@shamrocklogistics.ie",
        "phone": "+353 1 496 0000",
        "address": "Grand Canal Dock",
        "city": "Dublin",
        "country": "Ireland",
    },
    {
        "first_name": "Amina",
        "last_name": "Diallo",
        "email": "amina.diallo@sahelenergy.sn",
        "phone": "+221 33 821 0000",
        "address": "Boulevard de la République",
        "city": "Dakar",
        "country": "Senegal",
    },
    {
        "first_name": "Mateo",
        "last_name": "Silva",
        "email": "mateo.silva@atlanticosoftware.br",
        "phone": "+55 11 3000 4567",
        "address": "Avenida Paulista 1578",
        "city": "São Paulo",
        "country": "Brazil",
    },
    {
        "first_name": "Hannah",
        "last_name": "Schmidt",
        "email": "hannah.schmidt@alpinemedia.ch",
        "phone": "+41 44 211 5555",
        "address": "Bahnhofstrasse 45",
        "city": "Zurich",
        "country": "Switzerland",
    },
    {
        "first_name": "Kofi",
        "last_name": "Mensah",
        "email": "kofi.mensah@goldcoastfintech.gh",
        "phone": "+233 30 277 8899",
        "address": "Airport Residential Area",
        "city": "Accra",
        "country": "Ghana",
    },
    {
        "first_name": "Ingrid",
        "last_name": "Lindqvist",
        "email": "ingrid.lindqvist@balticbio.se",
        "phone": "+46 8 123 4567",
        "address": "Kungsgatan 12",
        "city": "Stockholm",
        "country": "Sweden",
    },
]


def seed_database():
    """Seed the database with sample customer data."""
    app = create_app()
    with app.app_context():
        # Initialize schema if table doesn't exist
        db.init_db()

        print(f"Connecting to database: {app.config['DATABASE']}")
        print(f"Seeding {len(SAMPLE_CUSTOMERS)} sample customers...")

        from app.validators import validate_customer_data

        count = 0
        for customer in SAMPLE_CUSTOMERS:
            is_valid, errors, cleaned = validate_customer_data(customer)
            if not is_valid:
                print(f"Validation error for {customer['first_name']}: {errors}", file=sys.stderr)
                continue
            repository.create_customer(cleaned)
            count += 1

        print(f"Successfully seeded {count} customer records into {app.config['DATABASE']}!")


if __name__ == "__main__":
    seed_database()
