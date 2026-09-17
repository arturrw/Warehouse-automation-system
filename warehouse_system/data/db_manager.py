"""
Database layer for the Warehouse.
"""

import hashlib
import sqlite3
from pathlib import Path
from typing import List, Optional

from warehouse_system.data.models import (
    CategoryStockSummary,
    DashboardStats,
    InventoryItem,
    StockMovement,
    UserRecord,
)
from warehouse_system.domain.role_policy import ADMIN_ROLE, VALID_ROLES


class DatabaseManager:
    """
    Manages SQLite persistence for users and inventory.

    Responsibilities:
        - Create and migrate the warehouse database schema
        - Seed default data required for login and dashboard
        - Authenticate users via verify_login()
    """

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"
    DEFAULT_ADMIN_ROLE = ADMIN_ROLE

    def __init__(self, db_path: str = "warehouse.db") -> None:
        """Initialize the database manager."""
        self.db_path = Path(db_path)
    def _connect(self) -> sqlite3.Connection:
        path = str(self.db_path)
        if path.startswith("file:"):
            connection = sqlite3.connect(path, uri=True)
        else:
            connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _hash_password(plain_password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

    def initialize_database(self) -> None:
        """
        Create the database file, tables and user if needed.

        Tables:
            Users: authentication and role based access
            Inventory: product catalog
            StockMovements: audit trail for inventory changes
        """
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Users (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username TEXT NOT NULL UNIQUE,
                    Password TEXT NOT NULL,
                    Role TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Inventory (
                    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Category TEXT NOT NULL,
                    Quantity INTEGER NOT NULL DEFAULT 0,
                    Price REAL NOT NULL DEFAULT 0.0
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS StockMovements (
                    MovementID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ItemID INTEGER,
                    ItemName TEXT NOT NULL,
                    QuantityDelta INTEGER NOT NULL,
                    ActionType TEXT NOT NULL,
                    Username TEXT NOT NULL,
                    RecordedAt TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )

            self._seed_default_admin(cursor)
            self._seed_sample_inventory(cursor)
            connection.commit()

    def _seed_default_admin(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM Users WHERE Username = ?",
            (self.DEFAULT_ADMIN_USERNAME,),
        )
        row = cursor.fetchone()
        if row and row["total"] == 0:
            cursor.execute(
                """
                INSERT INTO Users (Username, Password, Role)
                VALUES (?, ?, ?)
                """,
                (
                    self.DEFAULT_ADMIN_USERNAME,
                    self._hash_password(self.DEFAULT_ADMIN_PASSWORD),
                    self.DEFAULT_ADMIN_ROLE,
                ),
            )

    def verify_login(self, username: str, password: str) -> bool:
        """
        Verify if a user exists and  password is correct.

        Returns:
            True if a user record exists, otherwise false.
        """
        if not username.strip() or not password:
            return False

        password_hash = self._hash_password(password)

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT 1
                FROM Users
                WHERE Username = ? AND Password = ?
                """,
                (username.strip(), password_hash),
            )
            return cursor.fetchone() is not None

    def get_user_role(self, username: str) -> Optional[str]:

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT Role FROM Users WHERE Username = ?",
                (username.strip(),),
            )
            row = cursor.fetchone()
            return row["Role"] if row else None

    def list_users(self) -> List[UserRecord]:
        """Return all user accounts by username."""
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT ID, Username, Role
                FROM Users
                ORDER BY Username COLLATE NOCASE
                """
            )
            return [
                UserRecord(
                    user_id=row["ID"],
                    username=row["Username"],
                    role=row["Role"],
                )
                for row in cursor.fetchall()
            ]

    def add_user(self, username: str, password: str, role: str) -> Optional[int]:
        """
        Create a new user account.
        """
        username = username.strip()
        if not username or not password or role not in VALID_ROLES:
            return None

        with self._connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO Users (Username, Password, Role)
                    VALUES (?, ?, ?)
                    """,
                    (username, self._hash_password(password), role),
                )
                connection.commit()
                return int(cursor.lastrowid)
            except sqlite3.IntegrityError:
                return None

    def delete_user(self, user_id: int) -> bool:
        """
        Remove a user by primary key.

        The default admin account cannot be deleted.
        """
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT Username FROM Users WHERE ID = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row or row["Username"] == self.DEFAULT_ADMIN_USERNAME:
                return False

            cursor.execute("DELETE FROM Users WHERE ID = ?", (user_id,))
            connection.commit()
            return cursor.rowcount > 0

    def change_password(
        self, username: str, old_password: str, new_password: str
    ) -> bool:
        if not new_password or not self.verify_login(username, old_password):
            return False

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE Users
                SET Password = ?
                WHERE Username = ?
                """,
                (self._hash_password(new_password), username.strip()),
            )
            connection.commit()
            return cursor.rowcount > 0

    def _seed_sample_inventory(self, cursor: sqlite3.Cursor) -> None:
        """Inventory rows"""
        cursor.execute("SELECT COUNT(*) AS total FROM Inventory")
        row = cursor.fetchone()
        if row and row["total"] > 0:
            return

        sample_items = [
            ("Steel Shelving Unit", "Furniture", 12, 249.99),
            ("Barcode Scanner", "Electronics", 8, 89.50),
            ("Safety Gloves (Box)", "Safety", 45, 18.75),
            ("Pallet Jack", "Equipment", 3, 420.00),
            ("Shipping Labels (Roll)", "Supplies", 6, 12.99),
        ]
        cursor.executemany(
            """
            INSERT INTO Inventory (Name, Category, Quantity, Price)
            VALUES (?, ?, ?, ?)
            """,
            sample_items,
        )

    @staticmethod
    def _row_to_inventory_item(row: sqlite3.Row) -> InventoryItem:
        """SQLite row to an InventoryItem object."""
        return InventoryItem(
            item_id=row["ItemID"],
            name=row["Name"],
            category=row["Category"],
            quantity=row["Quantity"],
            price=float(row["Price"]),
        )

    def get_all_inventory(self) -> List[InventoryItem]:
        """Return inventory records ordered by name."""
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT ItemID, Name, Category, Quantity, Price
                FROM Inventory
                ORDER BY Name COLLATE NOCASE
                """
            )
            return [self._row_to_inventory_item(row) for row in cursor.fetchall()]

    def get_inventory_item(self, item_id: int) -> Optional[InventoryItem]:
        """Return a inventory item by ID or None if not found."""
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT ItemID, Name, Category, Quantity, Price
                FROM Inventory
                WHERE ItemID = ?
                """,
                (item_id,),
            )
            row = cursor.fetchone()
            return self._row_to_inventory_item(row) if row else None

    def _record_stock_movement(
        self,
        cursor: sqlite3.Cursor,
        item_id: Optional[int],
        item_name: str,
        quantity_delta: int,
        action_type: str,
        username: str,
    ) -> None:
        """Audit log row for an inventory change."""
        cursor.execute(
            """
            INSERT INTO StockMovements
                (ItemID, ItemName, QuantityDelta, ActionType, Username)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item_id, item_name, quantity_delta, action_type, username.strip()),
        )

    def add_inventory_item(
        self,
        name: str,
        category: str,
        quantity: int,
        price: float,
        username: str = "system",
    ) -> int:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO Inventory (Name, Category, Quantity, Price)
                VALUES (?, ?, ?, ?)
                """,
                (name.strip(), category.strip(), quantity, price),
            )
            item_id = int(cursor.lastrowid)
            self._record_stock_movement(
                cursor,
                item_id,
                name.strip(),
                quantity,
                "ADD",
                username,
            )
            connection.commit()
            return item_id

    def update_inventory_item(
        self,
        item_id: int,
        name: str,
        category: str,
        quantity: int,
        price: float,
        username: str = "system",
    ) -> bool:
        existing = self.get_inventory_item(item_id)
        if not existing:
            return False

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE Inventory
                SET Name = ?, Category = ?, Quantity = ?, Price = ?
                WHERE ItemID = ?
                """,
                (name.strip(), category.strip(), quantity, price, item_id),
            )
            quantity_delta = quantity - existing.quantity
            if quantity_delta != 0:
                self._record_stock_movement(
                    cursor,
                    item_id,
                    name.strip(),
                    quantity_delta,
                    "UPDATE",
                    username,
                )
            connection.commit()
            return cursor.rowcount > 0

    def delete_inventory_item(self, item_id: int, username: str = "system") -> bool:
        existing = self.get_inventory_item(item_id)
        if not existing:
            return False

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Inventory WHERE ItemID = ?", (item_id,))
            self._record_stock_movement(
                cursor,
                item_id,
                existing.name,
                -existing.quantity,
                "DELETE",
                username,
            )
            connection.commit()
            return cursor.rowcount > 0

    def get_stock_movements(self, limit: int = 200) -> List[StockMovement]:
        """Return recent stock, newest first."""
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT MovementID, ItemID, ItemName, QuantityDelta,
                       ActionType, Username, RecordedAt
                FROM StockMovements
                ORDER BY MovementID DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [
                StockMovement(
                    movement_id=row["MovementID"],
                    item_id=row["ItemID"],
                    item_name=row["ItemName"],
                    quantity_delta=row["QuantityDelta"],
                    action_type=row["ActionType"],
                    username=row["Username"],
                    recorded_at=row["RecordedAt"],
                )
                for row in cursor.fetchall()
            ]

    def get_dashboard_stats(self, low_stock_threshold: int = 10) -> DashboardStats:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_items,
                    COALESCE(SUM(Quantity), 0) AS total_units,
                    COALESCE(SUM(Quantity * Price), 0.0) AS total_stock_value,
                    COALESCE(SUM(CASE WHEN Quantity <= ? THEN 1 ELSE 0 END), 0)
                        AS low_stock_count
                FROM Inventory
                """,
                (low_stock_threshold,),
            )
            row = cursor.fetchone()

        return DashboardStats(
            total_items=int(row["total_items"]),
            total_units=int(row["total_units"]),
            total_stock_value=float(row["total_stock_value"]),
            low_stock_count=int(row["low_stock_count"]),
        )

    def get_stock_by_category(self) -> List[CategoryStockSummary]:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    Category,
                    COUNT(*) AS sku_count,
                    COALESCE(SUM(Quantity), 0) AS total_units,
                    COALESCE(SUM(Quantity * Price), 0.0) AS total_value
                FROM Inventory
                GROUP BY Category
                ORDER BY Category COLLATE NOCASE
                """
            )
            return [
                CategoryStockSummary(
                    category=row["Category"],
                    sku_count=int(row["sku_count"]),
                    total_units=int(row["total_units"]),
                    total_value=float(row["total_value"]),
                )
                for row in cursor.fetchall()
            ]

    def get_low_stock_items(self, threshold: int = 10) -> List[InventoryItem]:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT ItemID, Name, Category, Quantity, Price
                FROM Inventory
                WHERE Quantity <= ?
                ORDER BY Quantity ASC, Name COLLATE NOCASE
                """,
                (threshold,),
            )
            return [self._row_to_inventory_item(row) for row in cursor.fetchall()]
