"""
Login user interface
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dashboard_window import DashboardWindow
from db_manager import DatabaseManager
from models import UserSession


class LoginPage(QMainWindow):
    """
    Coordinates user input with DatabaseManager.verify_login() and displays success or failure feedback.
    """

    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()
        self._db = database_manager
        self._dashboard: DashboardWindow | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle("Warehouse Automation System - Login")
        self.setMinimumSize(420, 320)
        self.resize(480, 360)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(40, 36, 40, 36)
        root_layout.setSpacing(18)

        title_label = QLabel("Warehouse Automation")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Sign in to continue")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(14)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setClearButtonEnabled(True)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setClearButtonEnabled(True)
        self.password_input.returnPressed.connect(self._handle_login)

        form_layout.addRow("Username", self.username_input)
        form_layout.addRow("Password", self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self._handle_login)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.login_button)
        button_row.addStretch()

        root_layout.addWidget(title_label)
        root_layout.addWidget(subtitle_label)
        root_layout.addLayout(form_layout)
        root_layout.addLayout(button_row)
        root_layout.addStretch()

        self._apply_stylesheet()
        self.username_input.setFocus()

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f4f6f8;
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: 700;
                color: #1f2933;
            }
            QLabel#subtitleLabel {
                font-size: 13px;
                color: #52606d;
            }
            QLabel {
                color: #323f4b;
            }
            QLineEdit {
                padding: 8px 10px;
                border: 1px solid #cbd2d9;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1f2933;
                font-size: 13px;
                selection-background-color: #3e7bfa;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #3e7bfa;
                color: #1f2933;
            }
            QPushButton#loginButton {
                min-width: 120px;
                padding: 10px 18px;
                background-color: #3e7bfa;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#loginButton:hover {
                background-color: #2563eb;
            }
            QPushButton#loginButton:pressed {
                background-color: #1d4ed8;
            }
            """
        )

    def _handle_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Please enter both username and password.",
            )
            return

        if self._db.verify_login(username, password):
            role = self._db.get_user_role(username) or "User"
            session = UserSession(username=username, role=role)
            self._open_dashboard(session)
            self.password_input.clear()
            self.username_input.clear()
        else:
            QMessageBox.critical(
                self,
                "Login Failed",
                "Invalid username or password. Please try again.",
            )
            self.password_input.clear()
            self.password_input.setFocus()

    def _open_dashboard(self, session: UserSession) -> None:
        """Show the main dashboard"""
        self._dashboard = DashboardWindow(self._db, session)
        self._dashboard.logout_requested.connect(self._on_logout)
        self._dashboard.show()
        self.hide()

    def _on_logout(self) -> None:
        """Return to the login screen after sign out."""
        self._dashboard = None
        self.show()
        self.username_input.setFocus()
