"""
Unit tests for DatabaseManager.
"""

import uuid

import pytest

from warehouse_system.data.db_manager import DatabaseManager
from warehouse_system.domain.role_policy import ADMIN_ROLE, STAFF_ROLE


@pytest.fixture
def db() -> DatabaseManager:
    """In memory database."""
    db_uri = f"file:test_{uuid.uuid4().hex}?mode=memory&cache=shared"
    manager = DatabaseManager(db_uri)
    manager.initialize_database()
    yield manager


def test_default_admin_login(db: DatabaseManager) -> None:
    assert db.verify_login("admin", "admin123")
    assert db.get_user_role("admin") == ADMIN_ROLE


def test_invalid_login_rejected(db: DatabaseManager) -> None:
    assert not db.verify_login("admin", "wrong")
    assert not db.verify_login("", "admin123")


def test_add_and_list_users(db: DatabaseManager) -> None:
    user_id = db.add_user("staff1", "pass1234", STAFF_ROLE)
    assert user_id is not None
    users = {user.username: user for user in db.list_users()}
    assert "staff1" in users
    assert users["staff1"].role == STAFF_ROLE
    assert db.verify_login("staff1", "pass1234")


def test_duplicate_username_fails(db: DatabaseManager) -> None:
    assert db.add_user("dup", "pass1", STAFF_ROLE) is not None
    assert db.add_user("dup", "pass2", STAFF_ROLE) is None


def test_change_password(db: DatabaseManager) -> None:
    db.add_user("alice", "oldpass", STAFF_ROLE)
    assert db.verify_login("alice", "oldpass")
    assert db.change_password("alice", "oldpass", "newpass")
    assert not db.verify_login("alice", "oldpass")
    assert db.verify_login("alice", "newpass")


def test_cannot_delete_default_admin(db: DatabaseManager) -> None:
    users = db.list_users()
    admin = next(user for user in users if user.username == "admin")
    assert not db.delete_user(admin.user_id)


def test_inventory_crud_and_stats(db: DatabaseManager) -> None:
    item_id = db.add_inventory_item(
        "Test Widget", "Testing", 25, 9.99, username="admin"
    )
    items = db.get_all_inventory()
    assert any(item.item_id == item_id and item.name == "Test Widget" for item in items)

    assert db.update_inventory_item(
        item_id, "Test Widget", "Testing", 30, 9.99, username="admin"
    )
    updated = db.get_inventory_item(item_id)
    assert updated is not None
    assert updated.quantity == 30

    stats = db.get_dashboard_stats(low_stock_threshold=10)
    assert stats.total_items >= 1
    assert stats.total_units >= 30

    assert db.delete_inventory_item(item_id, username="admin")
    assert db.get_inventory_item(item_id) is None


def test_stock_by_category_and_low_stock(db: DatabaseManager) -> None:
    db.add_inventory_item("Low Item", "Demo", 2, 1.0, username="admin")
    summaries = db.get_stock_by_category()
    assert any(summary.category == "Demo" for summary in summaries)

    low = db.get_low_stock_items(threshold=10)
    assert any(item.name == "Low Item" for item in low)


def test_stock_movement_audit_log(db: DatabaseManager) -> None:
    item_id = db.add_inventory_item(
        "Audit Item", "Demo", 10, 5.0, username="tester"
    )
    db.update_inventory_item(
        item_id, "Audit Item", "Demo", 15, 5.0, username="tester"
    )
    db.delete_inventory_item(item_id, username="tester")

    movements = db.get_stock_movements()
    actions = [movement.action_type for movement in movements]
    assert "ADD" in actions
    assert "UPDATE" in actions
    assert "DELETE" in actions
    assert any(movement.username == "tester" for movement in movements)
