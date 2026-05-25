# Warehouse Automation System

Python desktop application for managing warehouse inventory, built for a university course project. The stack is **PyQt6** for the UI, **SQLite** for persistence, and a simple **OOP** layout: domain models, a database layer, and separate UI modules.

## Features

- **Login** with SHA-256 hashed passwords (default: `admin` / `admin123`, role: Admin)
- **Dashboard** with live SKU, unit, value, and low-stock metrics
- **Inventory** CRUD (Admin and Staff); user management remains Admin-only
- **Reports** - stock by category, low-stock list, stock movement audit log, CSV export
- **User management** (Admin only) - add and delete users with Admin or Staff roles
- **Settings** - change password for the signed-in account
- **Stock audit log** - every add, quantity update, and delete is recorded with user and timestamp

## Requirements

- Python 3.10 or newer
- Dependencies in `requirements.txt`

## Setup and run

```bash
cd "Warehouse automation system"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

On first run, `warehouse.db` is created in the project folder with sample inventory and the default admin user.

### Demo roles

1. Sign in as **admin** / **admin123** for full access.
2. Use **Users** to create a Staff account (e.g. `staff` / `staff123`).
3. Sign out and sign in as Staff to manage inventory and reports without the **Users** menu.

## Run tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests use a temporary database file and do not modify your production `warehouse.db`.

## Project structure

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `db_manager.py` | SQLite schema, auth, inventory CRUD, reports, audit log |
| `models.py` | Domain dataclasses |
| `role_policy.py` | Admin vs Staff permission helpers |
| `login_window.py` | Login screen |
| `dashboard_window.py` | Main shell and navigation |
| `home_page.py` | Dashboard metrics |
| `inventory_page.py` | Inventory table and dialogs |
| `reports_page.py` | Reports, audit log, CSV export |
| `users_page.py` | User management (Admin) |
| `settings_page.py` | Change password |
| `app_styles.py` | Fusion theme and stylesheets |
| `tests/test_db_manager.py` | Pytest coverage for the database layer |

## Database

Tables: `Users`, `Inventory`, `StockMovements`.

The default admin account cannot be deleted. Inventory changes made after this version was installed are written to `StockMovements`; older databases gain the table automatically on the next `initialize_database()` call.
