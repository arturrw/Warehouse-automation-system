"""
Entry point for the Warehouse.

Bootstraps the PyQt6 application, initializes persistence and displays the login window.
"""

import sys

from PyQt6.QtWidgets import QApplication

from app_styles import apply_app_theme
from db_manager import DatabaseManager
from login_window import LoginPage


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


if __name__ == "__main__":
    sys.exit(main())
