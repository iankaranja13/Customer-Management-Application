# Customer Management Application (CustomerHub)

A complete, production-grade Customer Management Application built for organizations to register, view, search, update, and manage customer records reliably.

Built with **Python**, **Flask**, **SQLite**, and vanilla web standards (HTML5/CSS3/minimal JS), this application is designed for simplicity, robustness, and zero external CDN or cloud dependencies.

---

## 1. Overview

**CustomerHub** provides an intuitive, responsive interface for managing customer information across an organization. It enforces strict server-side validation as the single source of truth, prevents duplicate email registrations, protects against SQL injection and cross-site scripting (XSS), includes session-based CSRF protection, and supports pagination, multi-field search, and sortable columns.

---

## 2. Features

- **Dashboard Metrics**: Live cards for Total Customers, Recently Added (last 30 days), and Cities Represented, all calculated from database records.
- **Customer Registration**: Register new customer profiles through a polished modal with field-level validation and real-time form feedback.
- **Directory & List View**: Professional directory with avatar initials, sortable columns (Customer, Email, City, Date Registered), and a compact per-row actions menu.
- **Pagination & Page Size**: Paginated view with selectable page size (10/25/50 records per page) and next/previous controls.
- **Multi-Field Search**: Live partial, case-insensitive search across First Name, Last Name, Full Name, Email, Phone, Address, City, and Country (`?q=term`), backed by a single server-side implementation.
- **Profile Drawer**: Slide-over customer profile showing avatar, ID, contact details, and registration date, with Edit and Delete actions.
- **Customer Updates**: Pre-filled edit form (modal or dedicated page) with self-ignoring duplicate email checks; customer IDs never change on update.
- **Safe Customer Deletion**: POST-only delete operation with an explicit confirmation dialog and irreversible action warnings; remaining IDs compact to stay sequential.
- **Toast Notifications**: Success and error feedback delivered as dismissible toast notifications.
- **CSRF Protection**: Integrated session-based CSRF validation across all state-modifying requests, including modal submissions.
- **Mobile-Responsive & Accessible**: Collapsible sidebar navigation, responsive customer cards on small screens, keyboard-dismissable dialogs, and visible focus states throughout.

---

## 3. Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+ & Flask | Application framework & routing |
| **Database** | SQLite3 | Persistent embedded relational database |
| **Templates** | Jinja2 | Safe HTML rendering with autoescaping |
| **Frontend** | Plain CSS3 & Vanilla JavaScript | Responsive styling and progressive UI enhancements (no CDNs) |
| **Testing** | pytest | Automated unit and integration test suite |

---

## 4. Setup & Running Locally

### Prerequisites
- Python 3.10 or newer
- Git

### Installation Steps

1. **Clone or navigate into the repository**:
   ```bash
   cd Customer-Management-Application
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   flask --app run.py init-db
   ```

5. **Seed sample data (15 realistic records)**:
   ```bash
   python seed.py
   ```

6. **Start the development server**:
   ```bash
   python run.py
   ```
   Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 5. Running the Test Suite

The test suite covers validators, repository operations, routes, edge cases, error handlers, and security constraints using an isolated temporary database for each run.

Run all tests:
```bash
pytest
```

Run with verbose test output:
```bash
pytest -v
```

---

## 5b. Deploying to Vercel

The project ships with a serverless entrypoint (`api/index.py`) and routing (`vercel.json`).

```bash
vercel env add SECRET_KEY production   # set a random secret for sessions/CSRF
vercel --prod
```

On cold start the app creates its SQLite database in `/tmp` (from a bundled copy when present, otherwise from `schema.sql` plus the demo seed data). Note that serverless `/tmp` storage is **ephemeral**: records added on the deployed site can disappear when instances recycle, so the deployment is suited for demos and evaluation. For persistent production data, migrate `repository.py` to a hosted database.

---

## 6. Project Structure

```
Customer-Management-Application/
├── app/
│   ├── __init__.py           # Application factory, CSRF protection, error handlers
│   ├── db.py                 # SQLite connection management and CLI commands
│   ├── repository.py         # Data access layer (parameterized CRUD & search)
│   ├── validators.py         # Pure validation functions and normalizers
│   ├── routes.py             # Flask Blueprint routes and request handlers
│   ├── templates/            # Jinja2 presentation templates
│   │   ├── base.html         # App shell: sidebar, topbar, toasts, modal/drawer roots
│   │   ├── customers/
│   │   │   ├── list.html     # Dashboard stats, directory, search, cards & pagination
│   │   │   ├── detail.html   # Customer profile detail view
│   │   │   ├── form.html     # Reusable registration and edit form
│   │   │   └── confirm_delete.html # Confirmation modal / page for deletion
│   │   └── errors/
│   │       ├── 400.html      # Bad request / CSRF failure page
│   │       ├── 404.html      # Friendly record not found page
│   │       └── 500.html      # Internal server error page
│   └── static/
│       ├── style.css         # Blue-and-slate SaaS design system, responsive
│       └── app.js            # Sidebar, modals, drawer, toasts, live search, validation
├── schema.sql                # SQLite database DDL schema and indexes
├── seed.py                   # Demo database seeder script (~15 records)
├── tests/                    # Comprehensive pytest test suite
│   ├── conftest.py           # Test fixtures with temporary isolated SQLite DB
│   ├── test_factory.py       # Factory and configuration tests
│   ├── test_db.py            # Database connection and teardown tests
│   ├── test_validators.py    # Unit tests for validation functions & edge cases
│   ├── test_repository.py    # Database CRUD and parameterized query tests
│   ├── test_routes.py        # Customer registration route tests
│   ├── test_view_customers.py# List, detail, pagination, and sorting tests
│   ├── test_search.py        # Multi-field search query tests
│   ├── test_update_customer.py# Edit route and self-ignoring duplicate checks
│   ├── test_delete_customer.py# POST-only delete, confirmation, ID compaction tests
│   ├── test_dashboard.py     # Dashboard stats and page-size selection tests
│   └── test_json_api.py      # JSON responses for modals/drawer tests
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Python dependencies (Flask, pytest)
├── run.py                    # Application launch script
├── README.md                 # Project documentation
├── DEMO_SCRIPT.md            # Step-by-step walkthrough script for evaluations
└── .gitignore                # Git ignore patterns (.db, .venv, __pycache__, etc.)
```

---

## 7. Database Schema

The SQLite schema uses parameterized queries for all operations and creates indexes on frequently searched columns.

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    phone TEXT NOT NULL,
    address TEXT,
    city TEXT,
    country TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_last_name ON customers(last_name);
```

---

## 8. Validation Rules Table

All user input is trimmed of whitespace prior to evaluation. Server-side validation is strictly enforced as the single source of truth.

| Field | Requirement | Constraints & Rules | Error Feedback |
|---|---|---|---|
| `first_name` | **Required** | 2–50 characters; Unicode letters, spaces, hyphens (`-`), apostrophes (`'`) only | Field-level error message; preserves typed input |
| `last_name` | **Required** | 2–50 characters; same character set rules as first name | Field-level error message; preserves typed input |
| `email` | **Required** | Valid email format (RFC); case-insensitive **unique**; max 254 characters | Rejects duplicates with friendly alert |
| `phone` | **Required** | 7–15 digits; optional leading `+`; allows spaces, dashes, parentheses during input; normalized before storing | Field-level error message |
| `address` | *Optional* | Maximum 200 characters | Length limit error |
| `city` | *Optional* | Maximum 60 characters | Length limit error |
| `country` | *Optional* | Maximum 60 characters | Length limit error |

---

## 9. Git Branching Strategy

The repository follows a clean Gitflow workflow:
- `main`: Production release branch. Only receives the final tested release merge and version tags (`v1.0.0`).
- `develop`: Integration branch where all completed features are merged with `--no-ff`.
- Feature branches (`feature/<name>`): Created off `develop` for each isolated piece of functionality.
- Commits follow the **Conventional Commits** specification (`feat:`, `test:`, `docs:`, `chore:`, `style:`, `refactor:`).

To inspect the complete branch and merge graph:
```bash
git log --oneline --graph --all
```
