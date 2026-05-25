"""
Role access for the Warehouse Automation System.
"""

ADMIN_ROLE = "Admin"
STAFF_ROLE = "Staff"
VALID_ROLES = (ADMIN_ROLE, STAFF_ROLE)


def is_admin(role: str) -> bool:
    """Return True when role admin."""
    return role == ADMIN_ROLE


def can_modify_inventory(role: str) -> bool:
    """Admin and staff may add, edit or delete inventory records."""
    return role in VALID_ROLES


def can_manage_users(role: str) -> bool:
    """Only admins may access the user management page."""
    return is_admin(role)
