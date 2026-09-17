"""
Application bootstrap for the Warehouse Automation System.

Wires the PyQt6 application, initializes persistence and shows the login window.
"""

import sys

from PyQt6.QtWidgets import QApplication

from warehouse_system.data.db_manager import DatabaseManager
from warehouse_system.ui.login_window import LoginPage
from warehouse_system.ui.styles import apply_app_theme


def main() -> int:
    """Initialize services and start the event loop."""
    app = QApplication(sys.argv)
    apply_app_theme(app)
    app.setApplicationName("Warehouse Automation System")
    app.setOrganizationName("UX-UI Course Project")

    database_manager = DatabaseManager()
    database_manager.initialize_database()

    login_window = LoginPage(database_manager)
    login_window.show()

    return app.exec()
