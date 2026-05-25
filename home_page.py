"""
Home dashboard page for the Warehouse Automation System.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from db_manager import DatabaseManager
from models import UserSession

LOW_STOCK_THRESHOLD = 10


class HomePage(QWidget):
    """
    Landing view after login with warehouse summary statistics.
    """

    def __init__(self, database_manager: DatabaseManager, session: UserSession) -> None:
        super().__init__()
        self._db = database_manager
        self._session = session
        self._stat_value_labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            f"Welcome back, {self._session.username}. "
            f"You are signed in as {self._session.role}."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        card_definitions = [
            ("total_items", "Total SKUs", "0"),
            ("total_units", "Units in Stock", "0"),
            ("total_stock_value", "Stock Value", "$0.00"),
            ("low_stock_count", "Low Stock Items", "0"),
        ]

        for index, (key, label_text, default_value) in enumerate(card_definitions):
            card, value_label = self._create_stat_card(label_text, default_value)
            self._stat_value_labels[key] = value_label
            row, col = divmod(index, 2)
            cards_layout.addWidget(card, row, col)

        low_stock_heading = QLabel(
            f"Low Stock (≤ {LOW_STOCK_THRESHOLD} units)"
        )
        low_stock_heading.setObjectName("pageSubtitle")

        self._low_stock_list = QLabel("Loading…")
        self._low_stock_list.setObjectName("pageSubtitle")
        self._low_stock_list.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(cards_layout)
        layout.addWidget(low_stock_heading)
        layout.addWidget(self._low_stock_list)
        layout.addStretch()

    def _create_stat_card(self, label_text: str, value_text: str) -> tuple[QFrame, QLabel]:
        """Single metric card widget."""
        card = QFrame()
        card.setObjectName("statCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(6)

        value_label = QLabel(value_text)
        value_label.setObjectName("statValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        caption_label = QLabel(label_text)
        caption_label.setObjectName("statLabel")

        card_layout.addWidget(value_label)
        card_layout.addWidget(caption_label)
        return card, value_label

    def refresh(self) -> None:
        """Reload dashboard from the database."""
        stats = self._db.get_dashboard_stats()
        self._stat_value_labels["total_items"].setText(str(stats.total_items))
        self._stat_value_labels["total_units"].setText(str(stats.total_units))
        self._stat_value_labels["total_stock_value"].setText(
            f"${stats.total_stock_value:,.2f}"
        )
        self._stat_value_labels["low_stock_count"].setText(str(stats.low_stock_count))

        low_stock_items = self._db.get_low_stock_items(LOW_STOCK_THRESHOLD)
        if low_stock_items:
            lines = [
                f"• {item.name} - {item.quantity} units ({item.category})"
                for item in low_stock_items
            ]
            self._low_stock_list.setText("\n".join(lines))
        else:
            self._low_stock_list.setText("No items at or below the low stock threshold.")
