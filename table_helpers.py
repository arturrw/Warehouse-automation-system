"""
Shared QTableWidget layout for dashboard pages.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QHeaderView,
    QSizePolicy,
    QTableWidget,
)


def configure_data_table(table: QTableWidget) -> None:
    """Read only table with columns stretched to the widget width."""
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setSizeAdjustPolicy(
        QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored
    )
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header.setStretchLastSection(True)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)


def configure_full_page_table(table: QTableWidget) -> None:
    """Table expand to fill the remaining page area."""
    configure_data_table(table)
    table.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )


def sync_table_height(
    table: QTableWidget, row_count: int, max_visible_rows: int
) -> None:
    """Fixed height for stacked report tables"""
    if row_count > 0:
        table.resizeRowsToContents()

    rows_shown = min(row_count, max_visible_rows) if row_count else 1
    header_height = table.horizontalHeader().height()
    if row_count > 0:
        body_height = sum(table.rowHeight(row) for row in range(rows_shown))
    else:
        body_height = table.verticalHeader().defaultSectionSize()

    frame = table.frameWidth() * 2
    table.setFixedHeight(header_height + body_height + frame + 10)
    table.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
    )
    table.setVerticalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded
        if row_count > max_visible_rows
        else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
