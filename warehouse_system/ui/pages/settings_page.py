"""
Settings page
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from warehouse_system.data.db_manager import DatabaseManager
from warehouse_system.data.models import UserSession


class SettingsPage(QWidget):
    """Account settings and password change."""

    def __init__(
        self, database_manager: DatabaseManager, session: UserSession
    ) -> None:
        super().__init__()
        self._db = database_manager
        self._session = session
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            f"Signed in as {self._session.username} ({self._session.role}). "
            "Update your account password."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        for field in (
            self.current_password_input,
            self.new_password_input,
            self.confirm_password_input,
        ):
            field.setFixedHeight(32)
            field.setMinimumWidth(540)
            field.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )

        form_layout.addRow("Current Password", self.current_password_input)
        form_layout.addRow("New Password", self.new_password_input)
        form_layout.addRow("Confirm New Password", self.confirm_password_input)

        self.change_button = QPushButton("Change Password")
        self.change_button.setProperty("class", "actionButton")
        self.change_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_button.clicked.connect(self._change_password)
        self.change_button.setFixedHeight(34)
        self.change_button.setMinimumWidth(240)
        self.change_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        button_row = QHBoxLayout()
        button_row.addWidget(self.change_button)
        button_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form_layout)
        layout.addLayout(button_row)
        layout.addStretch()

    def refresh(self) -> None:
        """Clear password fields when the page is shown."""
        self.current_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()

    def _change_password(self) -> None:
        current = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm = self.confirm_password_input.text()

        if not current or not new_password:
            QMessageBox.warning(
                self,
                "Change Password",
                "Enter your current password and a new password.",
            )
            return

        if new_password != confirm:
            QMessageBox.warning(
                self,
                "Change Password",
                "New password do not match.",
            )
            return

        if len(new_password) < 4:
            QMessageBox.warning(
                self,
                "Change Password",
                "New password must be at least 4 characters.",
            )
            return

        if self._db.change_password(
            self._session.username, current, new_password
        ):
            QMessageBox.information(
                self,
                "Change Password",
                "Your password has been updated successfully.",
            )
            self.refresh()
            return

        QMessageBox.warning(
            self,
            "Change Password",
            "Could not update password. Try again.",
        )
