"""
Reports and analytics
"""

import csv
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from warehouse_system.data.db_manager import DatabaseManager
from warehouse_system.ui.table_helpers import configure_data_table, sync_table_height


class ReportsPage(QWidget):
    """
    Displays aggregate inventory reports and supports CSV export.
    """

    LOW_STOCK_THRESHOLD = 10

    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()
        self._db = database_manager
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Reports")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Stock summaries by category, low stock items and CSV export."
        )
        subtitle.setObjectName("pageSubtitle")

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.setProperty("class", "actionButton")
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_button.clicked.connect(self._export_csv)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "secondaryButton")
        self.refresh_button.clicked.connect(self.refresh)

        toolbar.addStretch()
        toolbar.addWidget(self.export_button)
        toolbar.addWidget(self.refresh_button)

        self.category_table = QTableWidget(0, 4)
        self.category_table.setHorizontalHeaderLabels(
            ["Category", "SKUs", "Units", "Value"]
        )
        configure_data_table(self.category_table)

        self.low_stock_table = QTableWidget(0, 4)
        self.low_stock_table.setHorizontalHeaderLabels(
            ["Name", "Category", "Quantity", "Price"]
        )
        configure_data_table(self.low_stock_table)

        self.audit_table = QTableWidget(0, 6)
        self.audit_table.setHorizontalHeaderLabels(
            ["When", "Item", "Delta", "Action", "User", "Item ID"]
        )
        configure_data_table(self.audit_table)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(toolbar)
        layout.addWidget(
            self._report_section(
                "Stock by Category",
                self.category_table,
            )
        )
        layout.addWidget(
            self._report_section(
                f"Low Stock (≤ {self.LOW_STOCK_THRESHOLD} units)",
                self.low_stock_table,
            )
        )
        layout.addWidget(
            self._report_section(
                "Stock movement audit log",
                self.audit_table,
            )
        )
        layout.addStretch()

    @staticmethod
    def _report_section(title: str, table: QTableWidget) -> QWidget:
        """Group a section heading and table so layout spacing stays consistent."""
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(8)

        heading = QLabel(title)
        heading.setObjectName("pageSubtitle")
        section_layout.addWidget(heading)
        section_layout.addWidget(table)
        return section

    def refresh(self) -> None:
        """Reload report tables"""
        summaries = self._db.get_stock_by_category()
        self.category_table.setRowCount(len(summaries))
        for row_index, summary in enumerate(summaries):
            values = [
                summary.category,
                str(summary.sku_count),
                str(summary.total_units),
                f"${summary.total_value:,.2f}",
            ]
            for col_index, value in enumerate(values):
                self.category_table.setItem(
                    row_index, col_index, QTableWidgetItem(value)
                )
        sync_table_height(self.category_table, len(summaries), max_visible_rows=6)

        low_stock = self._db.get_low_stock_items(self.LOW_STOCK_THRESHOLD)
        self.low_stock_table.setRowCount(len(low_stock))
        for row_index, item in enumerate(low_stock):
            values = [
                item.name,
                item.category,
                str(item.quantity),
                f"${item.price:,.2f}",
            ]
            for col_index, value in enumerate(values):
                self.low_stock_table.setItem(
                    row_index, col_index, QTableWidgetItem(value)
                )
        sync_table_height(self.low_stock_table, len(low_stock), max_visible_rows=6)

        movements = self._db.get_stock_movements()
        self.audit_table.setRowCount(len(movements))
        for row_index, movement in enumerate(movements):
            item_id_text = (
                str(movement.item_id) if movement.item_id is not None else "-"
            )
            delta_text = (
                f"+{movement.quantity_delta}"
                if movement.quantity_delta > 0
                else str(movement.quantity_delta)
            )
            values = [
                movement.recorded_at,
                movement.item_name,
                delta_text,
                movement.action_type,
                movement.username,
                item_id_text,
            ]
            for col_index, value in enumerate(values):
                self.audit_table.setItem(
                    row_index, col_index, QTableWidgetItem(value)
                )
        sync_table_height(self.audit_table, len(movements), max_visible_rows=8)

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reports",
            str(Path.home() / "warehouse_report.csv"),
            "CSV Files (*.csv)",
        )
        if not path:
            return

        try:
            summaries = self._db.get_stock_by_category()
            low_stock = self._db.get_low_stock_items(self.LOW_STOCK_THRESHOLD)
            movements = self._db.get_stock_movements()
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Stock by Category"])
                writer.writerow(["Category", "SKUs", "Units", "Value"])
                for summary in summaries:
                    writer.writerow(
                        [
                            summary.category,
                            summary.sku_count,
                            summary.total_units,
                            f"{summary.total_value:.2f}",
                        ]
                    )
                writer.writerow([])
                writer.writerow([f"Low Stock (<= {self.LOW_STOCK_THRESHOLD} units)"])
                writer.writerow(["Name", "Category", "Quantity", "Price"])
                for item in low_stock:
                    writer.writerow(
                        [
                            item.name,
                            item.category,
                            item.quantity,
                            f"{item.price:.2f}",
                        ]
                    )
                writer.writerow([])
                writer.writerow(["Stock Movement Audit Log"])
                writer.writerow(
                    ["When", "Item", "Delta", "Action", "User", "Item ID"]
                )
                for movement in movements:
                    writer.writerow(
                        [
                            movement.recorded_at,
                            movement.item_name,
                            movement.quantity_delta,
                            movement.action_type,
                            movement.username,
                            movement.item_id if movement.item_id is not None else "",
                        ]
                    )
            QMessageBox.information(
                self, "Export Complete", f"Report saved to:\n{path}"
            )
        except OSError as exc:
            QMessageBox.warning(
                self, "Export Failed", f"Could not write the file:\n{exc}"
            )
