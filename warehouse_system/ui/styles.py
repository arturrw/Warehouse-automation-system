"""
Qt stylesheets for a desktop appearance.
"""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


def apply_app_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    text = QColor("#1f2933")
    base = QColor("#ffffff")
    window = QColor("#f4f6f8")

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f9fafb"))
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, base)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#9aa5b1"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3e7bfa"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

    app.setPalette(palette)


DASHBOARD_STYLESHEET = """
QMainWindow#dashboardWindow {
    background-color: #f4f6f8;
}
QFrame#sidebar {
    background-color: #1f2933;
    border: none;
}
QLabel#sidebarTitle {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    padding: 8px 4px 16px 4px;
}
QLabel#sidebarUser {
    color: #9aa5b1;
    font-size: 12px;
    padding-bottom: 12px;
}
QPushButton.navButton {
    text-align: left;
    padding: 10px 14px;
    border: none;
    border-radius: 6px;
    color: #cbd2d9;
    background: transparent;
    font-size: 13px;
}
QPushButton.navButton:hover {
    background-color: #323f4b;
    color: #ffffff;
}
QPushButton.navButton[active="true"] {
    background-color: #3e7bfa;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#logoutButton {
    text-align: left;
    padding: 10px 14px;
    border: none;
    border-radius: 6px;
    color: #ffb8b8;
    background: transparent;
    font-size: 13px;
}
QPushButton#logoutButton:hover {
    background-color: #4a3030;
}
QFrame#contentFrame {
    background-color: #f4f6f8;
}
QLabel#pageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #1f2933;
}
QLabel#pageSubtitle {
    font-size: 13px;
    color: #52606d;
}
QFrame#statCard {
    background-color: #ffffff;
    border: 1px solid #e4e7eb;
    border-radius: 10px;
}
QLabel.statValue {
    font-size: 24px;
    font-weight: 700;
    color: #1f2933;
}
QLabel.statLabel {
    font-size: 12px;
    color: #52606d;
}
QTableWidget {
    background-color: #ffffff;
    color: #1f2933;
    border: 1px solid #e4e7eb;
    border-radius: 8px;
    gridline-color: #e4e7eb;
    font-size: 13px;
    selection-background-color: #dbeafe;
    selection-color: #1f2933;
}
QTableWidget::item {
    color: #1f2933;
    background-color: #ffffff;
}
QTableWidget::item:alternate {
    color: #1f2933;
    background-color: #f9fafb;
}
QTableWidget::item:selected {
    color: #1f2933;
    background-color: #dbeafe;
}
QLineEdit, QSpinBox, QComboBox {
    color: #1f2933;
    background-color: #ffffff;
    border: 1px solid #cbd2d9;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    min-height: 20px;
    max-height: 32px;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    color: #1f2933;
    border-color: #3e7bfa;
}
QHeaderView::section {
    background-color: #f0f4f8;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #e4e7eb;
    font-weight: 600;
    color: #323f4b;
}
QPushButton.actionButton {
    padding: 8px 14px;
    background-color: #3e7bfa;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
    max-height: 36px;
}
QPushButton.actionButton:hover {
    background-color: #2563eb;
}
QPushButton.secondaryButton {
    padding: 8px 14px;
    background-color: #ffffff;
    color: #323f4b;
    border: 1px solid #cbd2d9;
    border-radius: 6px;
    font-size: 13px;
    min-height: 20px;
    max-height: 36px;
}
QPushButton.secondaryButton:hover {
    background-color: #f0f4f8;
}
QPushButton.dangerButton {
    padding: 8px 14px;
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
    max-height: 36px;
}
QPushButton.dangerButton:hover {
    background-color: #dc2626;
}
"""
