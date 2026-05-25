"""
Inventory management page.
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QSizePolicy,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db_manager import DatabaseManager
from models import InventoryItem, UserSession
from role_policy import can_modify_inventory
from table_helpers import configure_full_page_table


class InventoryItemDialog(QDialog):
    """Сreating or editing an inventory item."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        item: Optional[InventoryItem] = None,
    ) -> None:
        super().__init__(parent)
        self._item = item
        self._build_ui()
        if item:
            self._populate_fields(item)

    def _build_ui(self) -> None:
        self.setWindowTitle("Edit Item" if self._item else "Add Item")
        self.setMinimumWidth(360)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1_000_000)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")

        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Category", self.category_input)
        form_layout.addRow("Quantity", self.quantity_input)
        form_layout.addRow("Price", self.price_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        root_layout = QVBoxLayout(self)
        root_layout.addLayout(form_layout)
        root_layout.addWidget(buttons)

    def _populate_fields(self, item: InventoryItem) -> None:
        self.name_input.setText(item.name)
        self.category_input.setText(item.category)
        self.quantity_input.setValue(item.quantity)
        self.price_input.setText(f"{item.price:.2f}")

    def _validate_and_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Name is required.")
            return
        if not self.category_input.text().strip():
            QMessageBox.warning(self, "Validation", "Category is required.")
            return
        try:
            price = float(self.price_input.text().strip())
            if price < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validation", "Enter a valid price (0 or greater).")
            return
        self.accept()

    def get_form_data(self) -> tuple[str, str, int, float]:
        """Return validated field values after the dialog is accepted."""
        return (
            self.name_input.text().strip(),
            self.category_input.text().strip(),
            self.quantity_input.value(),
            float(self.price_input.text().strip()),
        )


class InventoryPage(QWidget):
    """
    Interface for warehouse inventory, this class only manages UI state.
    """

    def __init__(
        self, database_manager: DatabaseManager, session: UserSession
    ) -> None:
        super().__init__()
        self._db = database_manager
        self._session = session
        self._can_modify = can_modify_inventory(session.role)
        self._build_ui()
        self._apply_role_restrictions()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Inventory")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "View, add, update and remove warehouse stock items."
        )
        subtitle.setObjectName("pageSubtitle")

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search by name or category...")
        self._search_input.textChanged.connect(self._apply_filter)
        self._search_input.setFixedHeight(32)
        self._search_input.setMinimumWidth(540)
        self._search_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._all_items: list[InventoryItem] = []

        search_row = QHBoxLayout()
        search_row.addWidget(self._search_input, stretch=1)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.add_button = QPushButton("Add Item")
        self.add_button.setProperty("class", "actionButton")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.clicked.connect(self._add_item)

        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.setProperty("class", "secondaryButton")
        self.edit_button.clicked.connect(self._edit_item)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setProperty("class", "dangerButton")
        self.delete_button.clicked.connect(self._delete_item)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "secondaryButton")
        self.refresh_button.clicked.connect(self.refresh)

        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_button)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Category", "Quantity", "Price"]
        )
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        configure_full_page_table(self.table)
        self.table.setColumnHidden(0, False)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(search_row)
        layout.addLayout(toolbar)
        layout.addWidget(self.table, stretch=1)

    def _apply_role_restrictions(self) -> None:
        """Disable CRUD controls when the signed in role cannot modify inventory."""
        if not self._can_modify:
            self.add_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def refresh(self) -> None:
        """Reload inventory table."""
        self._all_items = self._db.get_all_inventory()
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Show inventory rows matching the search."""
        query = self._search_input.text().strip().lower()
        if query:
            items = [
                item
                for item in self._all_items
                if query in item.name.lower() or query in item.category.lower()
            ]
        else:
            items = self._all_items

        self.table.setRowCount(len(items))
        for row_index, item in enumerate(items):
            values = [
                str(item.item_id),
                item.name,
                item.category,
                str(item.quantity),
                f"${item.price:,.2f}",
            ]
            for col_index, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if col_index == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, item.item_id)
                self.table.setItem(row_index, col_index, cell)

    def _selected_item(self) -> Optional[InventoryItem]:
        row = self.table.currentRow()
        if row < 0:
            return None

        try:
            item_id = int(self.table.item(row, 0).text())
            name = self.table.item(row, 1).text()
            category = self.table.item(row, 2).text()
            quantity = int(self.table.item(row, 3).text())
            price_text = self.table.item(row, 4).text().replace("$", "").replace(",", "")
            price = float(price_text)
        except (AttributeError, ValueError, TypeError):
            return None

        return InventoryItem(item_id, name, category, quantity, price)

    def _add_item(self) -> None:
        if not self._can_modify:
            return
        dialog = InventoryItemDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name, category, quantity, price = dialog.get_form_data()
        self._db.add_inventory_item(
            name, category, quantity, price, username=self._session.username
        )
        self.refresh()

    def _edit_item(self) -> None:
        if not self._can_modify:
            return
        item = self._selected_item()
        if not item:
            QMessageBox.information(self, "Edit Item", "Select an item to edit.")
            return

        dialog = InventoryItemDialog(self, item=item)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name, category, quantity, price = dialog.get_form_data()
        updated = self._db.update_inventory_item(
            item.item_id,
            name,
            category,
            quantity,
            price,
            username=self._session.username,
        )
        if not updated:
            QMessageBox.warning(self, "Edit Item", "Could not update the selected item.")
            return
        self.refresh()

    def _delete_item(self) -> None:
        if not self._can_modify:
            return
        item = self._selected_item()
        if not item:
            QMessageBox.information(self, "Delete Item", "Select an item to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Delete Item",
            f"Delete '{item.name}' from inventory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        deleted = self._db.delete_inventory_item(
            item.item_id, username=self._session.username
        )
        if not deleted:
            QMessageBox.warning(self, "Delete Item", "Could not delete the selected item.")
            return
        self.refresh()
