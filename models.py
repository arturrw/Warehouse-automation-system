"""
Domain models for the Warehouse.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserSession:
    """User context."""
    username: str
    role: str


@dataclass(frozen=True)
class InventoryItem:
    """Single inventory record from the catalog."""

    item_id: int
    name: str
    category: str
    quantity: int
    price: float


@dataclass(frozen=True)
class DashboardStats:
    """Summary metrics displayed on the home dashboard."""

    total_items: int
    total_units: int
    total_stock_value: float
    low_stock_count: int


@dataclass(frozen=True)
class UserRecord:
    """User account row from the users table."""

    user_id: int
    username: str
    role: str


@dataclass(frozen=True)
class CategoryStockSummary:
    """Inventory metrics grouped by category."""

    category: str
    sku_count: int
    total_units: int
    total_value: float


@dataclass(frozen=True)
class StockMovement:
    """Stock change recorded in the audit log."""

    movement_id: int
    item_id: Optional[int]
    item_name: str
    quantity_delta: int
    action_type: str
    username: str
    recorded_at: str
