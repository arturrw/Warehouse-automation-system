"""
Shell after authentication.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app_styles import DASHBOARD_STYLESHEET
from db_manager import DatabaseManager
from home_page import HomePage
from inventory_page import InventoryPage
from models import UserSession
from reports_page import ReportsPage
from role_policy import can_manage_users
from settings_page import SettingsPage
from users_page import UsersPage


class DashboardWindow(QMainWindow):
    """
    Primary shell with sidebar navigation and stacked content pages.
    """

    logout_requested = pyqtSignal()

    def __init__(self, database_manager: DatabaseManager, session: UserSession) -> None:
        super().__init__()
        self._db = database_manager
        self._session = session
        self._nav_buttons: list[QPushButton] = []
        self._nav_keys: list[str] = []
        self._pages_by_key: dict[str, QWidget] = {}
        self._build_ui()
        self._navigate_to("home")

    def _build_ui(self) -> None:
        self.setObjectName("dashboardWindow")
        self.setWindowTitle("Warehouse Automation System - Dashboard")
        self.setMinimumSize(960, 600)
        self.resize(1100, 700)
        self.setStyleSheet(DASHBOARD_STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")

        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.page_stack = QStackedWidget()
        content_layout.addWidget(self.page_stack)

        self._register_pages()
        root_layout.addWidget(sidebar)
        root_layout.addWidget(content_frame, stretch=1)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)

        title = QLabel("Warehouse")
        title.setObjectName("sidebarTitle")

        user_label = QLabel(f"{self._session.username}\n{self._session.role}")
        user_label.setObjectName("sidebarUser")
        user_label.setWordWrap(True)

        nav_items = [
            ("home", "Home"),
            ("inventory", "Inventory"),
            ("reports", "Reports"),
        ]
        if can_manage_users(self._session.role):
            nav_items.append(("users", "Users"))
        nav_items.append(("settings", "Settings"))

        self._nav_keys = [key for key, _ in nav_items]

        for key, label in nav_items:
            button = QPushButton(label)
            button.setProperty("class", "navButton")
            button.setProperty("active", "false")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, page_key=key: self._navigate_to(page_key)
            )
            self._nav_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()

        logout_button = QPushButton("Logout")
        logout_button.setObjectName("logoutButton")
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.clicked.connect(self._handle_logout)
        layout.addWidget(logout_button)

        layout.insertWidget(0, title)
        layout.insertWidget(1, user_label)
        return sidebar

    def _register_pages(self) -> None:
        """Content pages."""
        pages: dict[str, QWidget] = {
            "home": HomePage(self._db, self._session),
            "inventory": InventoryPage(self._db, self._session),
            "reports": ReportsPage(self._db),
            "settings": SettingsPage(self._db, self._session),
        }
        if can_manage_users(self._session.role):
            pages["users"] = UsersPage(self._db, self._session)

        for page in pages.values():
            self.page_stack.addWidget(page)

        self._pages_by_key = pages

    def _navigate_to(self, page_key: str) -> None:
        """Switch the visible page and highlight the active navigation button."""
        page = self._pages_by_key.get(page_key)
        if page is None:
            return

        self.page_stack.setCurrentWidget(page)
        if hasattr(page, "refresh"):
            page.refresh()

        for button, key in zip(self._nav_buttons, self._nav_keys):
            button.setProperty("active", "true" if key == page_key else "false")
            button.style().unpolish(button)
            button.style().polish(button)

    def _handle_logout(self) -> None:
        self.logout_requested.emit()
        self.close()
