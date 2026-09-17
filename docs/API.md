# API Reference

This is a desktop application, not a web service — there is no HTTP/REST API.
"API" here means the internal Python interface that the UI layer (`warehouse_system/ui`)
is allowed to call. It is entirely `warehouse_system.data.db_manager.DatabaseManager`,
plus the read-only helpers in `warehouse_system.domain.role_policy`. Everything below
is stable within a layer and is what you should extend when adding a feature.

## `warehouse_system.data.db_manager.DatabaseManager`

```python
from warehouse_system.data.db_manager import DatabaseManager

db = DatabaseManager("warehouse.db")   # or a sqlite3 URI, e.g. "file:...?mode=memory&cache=shared"
db.initialize_database()
```

### Setup

| Method | Description |
|---|---|
| `initialize_database() -> None` | Creates `Users`, `Inventory`, `StockMovements` if missing, seeds the default admin (`admin` / `admin123`) and sample inventory rows. Safe to call on every startup. |

### Authentication & users

| Method | Description |
|---|---|
| `verify_login(username: str, password: str) -> bool` | SHA-256 hashes `password` and checks it against the stored hash. |
| `get_user_role(username: str) -> Optional[str]` | Returns `"Admin"` / `"Staff"`, or `None` if the user doesn't exist. |
| `list_users() -> List[UserRecord]` | All accounts, ordered by username (case-insensitive). |
| `add_user(username: str, password: str, role: str) -> Optional[int]` | Creates a user. Returns the new `ID`, or `None` if the username exists or `role` isn't in `role_policy.VALID_ROLES`. |
| `delete_user(user_id: int) -> bool` | Deletes a user. Always fails for the default admin account. |
| `change_password(username: str, old_password: str, new_password: str) -> bool` | Verifies `old_password` before updating. |

### Inventory

| Method | Description |
|---|---|
| `get_all_inventory() -> List[InventoryItem]` | All items, ordered by name. |
| `get_inventory_item(item_id: int) -> Optional[InventoryItem]` | Single item lookup. |
| `add_inventory_item(name, category, quantity, price, username="system") -> int` | Inserts a row and records an `"ADD"` stock movement. Returns the new `ItemID`. |
| `update_inventory_item(item_id, name, category, quantity, price, username="system") -> bool` | Updates a row. Records an `"UPDATE"` movement only if `quantity` changed. Returns `False` if `item_id` doesn't exist. |
| `delete_inventory_item(item_id, username="system") -> bool` | Deletes a row and records a `"DELETE"` movement with the negated quantity. |

### Reports

| Method | Description |
|---|---|
| `get_dashboard_stats(low_stock_threshold: int = 10) -> DashboardStats` | Total SKUs, total units, total stock value, low-stock count. |
| `get_stock_by_category() -> List[CategoryStockSummary]` | SKU count, units and value grouped by `Category`. |
| `get_low_stock_items(threshold: int = 10) -> List[InventoryItem]` | Items at or below `threshold`, ascending by quantity. |
| `get_stock_movements(limit: int = 200) -> List[StockMovement]` | Most recent audit log entries first. |

All write methods commit internally — callers never manage transactions or
connections themselves.

## `warehouse_system.data.models`

Frozen (immutable) dataclasses returned by `DatabaseManager`. They are the only
shape of data that crosses from the data layer into the UI layer.

| Dataclass | Fields |
|---|---|
| `UserSession` | `username: str`, `role: str` — the signed-in user, held by `DashboardWindow` and passed to every page. |
| `UserRecord` | `user_id: int`, `username: str`, `role: str` |
| `InventoryItem` | `item_id: int`, `name: str`, `category: str`, `quantity: int`, `price: float` |
| `DashboardStats` | `total_items: int`, `total_units: int`, `total_stock_value: float`, `low_stock_count: int` |
| `CategoryStockSummary` | `category: str`, `sku_count: int`, `total_units: int`, `total_value: float` |
| `StockMovement` | `movement_id: int`, `item_id: Optional[int]`, `item_name: str`, `quantity_delta: int`, `action_type: str`, `username: str`, `recorded_at: str` |

## `warehouse_system.domain.role_policy`

Pure functions, no side effects, safe to call from anywhere (including tests
without a database).

| Function | Description |
|---|---|
| `is_admin(role: str) -> bool` | `role == "Admin"` |
| `can_modify_inventory(role: str) -> bool` | `True` for both `"Admin"` and `"Staff"` |
| `can_manage_users(role: str) -> bool` | `True` only for `"Admin"` |

Constants: `ADMIN_ROLE`, `STAFF_ROLE`, `VALID_ROLES = (ADMIN_ROLE, STAFF_ROLE)`.

## Extending the API

Adding a feature that needs new persistence:

1. Add the SQL to `DatabaseManager` (a new method, or a new table created in
   `initialize_database`).
2. Add a matching frozen dataclass to `models.py` if the method returns rows.
3. If the feature is role-gated, add a check to `role_policy.py` rather than
   inlining a role string comparison in the UI.
4. Call the new method from a page in `warehouse_system/ui/pages/`.
5. Cover the data-layer change with a test in `tests/test_db_manager.py` — see
   [CONTRIBUTING.md](../CONTRIBUTING.md#tests).
