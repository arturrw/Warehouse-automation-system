"""
User management page (Admin only)
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from warehouse_system.data.db_manager import DatabaseManager
from warehouse_system.data.models import UserRecord, UserSession
from warehouse_system.domain.role_policy import VALID_ROLES
from warehouse_system.ui.table_helpers import configure_full_page_table


class AddUserDialog(QDialog):
    """Create a new user account."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle("Add User")
        self.setMinimumWidth(360)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_input = QComboBox()
        self.role_input.addItems(list(VALID_ROLES))

        form_layout.addRow("Username", self.username_input)
        form_layout.addRow("Password", self.password_input)
        form_layout.addRow("Role", self.role_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        root_layout = QVBoxLayout(self)
        root_layout.addLayout(form_layout)
        root_layout.addWidget(buttons)

    def _validate_and_accept(self) -> None:
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Validation", "Username is required.")
            return
        if not self.password_input.text():
            QMessageBox.warning(self, "Validation", "Password is required.")
            return
        self.accept()

    def get_form_data(self) -> tuple[str, str, str]:
        """Return username, password and role."""
        return (
            self.username_input.text().strip(),
            self.password_input.text(),
            self.role_input.currentText(),
        )


class UsersPage(QWidget):
    """
    CRUD interface for user accounts.
    """

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

        title = QLabel("User Management")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Add and remove warehouse user accounts (Admin only).")
        subtitle.setObjectName("pageSubtitle")

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.add_button = QPushButton("Add User")
        self.add_button.setProperty("class", "actionButton")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.clicked.connect(self._add_user)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setProperty("class", "dangerButton")
        self.delete_button.clicked.connect(self._delete_user)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "secondaryButton")
        self.refresh_button.clicked.connect(self.refresh)

        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_button)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role"])
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        configure_full_page_table(self.table)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(toolbar)
        layout.addWidget(self.table, stretch=1)

    def refresh(self) -> None:
        users = self._db.list_users()
        self.table.setRowCount(len(users))

        for row_index, user in enumerate(users):
            values = [str(user.user_id), user.username, user.role]
            for col_index, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if col_index == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, user.user_id)
                self.table.setItem(row_index, col_index, cell)

    def _selected_user(self) -> Optional[UserRecord]:
        row = self.table.currentRow()
        if row < 0:
            return None

        try:
            user_id = int(self.table.item(row, 0).text())
            username = self.table.item(row, 1).text()
            role = self.table.item(row, 2).text()
        except (AttributeError, ValueError, TypeError):
            return None

        return UserRecord(user_id=user_id, username=username, role=role)

    def _add_user(self) -> None:
        dialog = AddUserDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        username, password, role = dialog.get_form_data()
        user_id = self._db.add_user(username, password, role)
        if user_id is None:
            QMessageBox.warning(
                self,
                "Add User",
                "Could not create user. The username may already exist.",
            )
            return
        self.refresh()

    def _delete_user(self) -> None:
        user = self._selected_user()
        if not user:
            QMessageBox.information(
                self, "Delete User", "Select a user to delete."
            )
            return

        if user.username == self._db.DEFAULT_ADMIN_USERNAME:
            QMessageBox.warning(
                self,
                "Delete User",
                "The default admin account cannot be deleted.",
            )
            return

        if user.username == self._session.username:
            QMessageBox.warning(
                self,
                "Delete User",
                "You cannot delete your own account while signed in.",
            )
            return

        confirm = QMessageBox.question(
            self,
            "Delete User",
            f"Delete user '{user.username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if not self._db.delete_user(user.user_id):
            QMessageBox.warning(self, "Delete User", "Could not delete the user.")
            return
        self.refresh()
