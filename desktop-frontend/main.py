"""
Chemical Equipment Parameter Visualizer - Desktop Application
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from services.api_client import ApiClient
from ui.main_window import MainWindow

QSS = """
QMainWindow { background: #f5f7fa; }
QTabWidget::pane { border: 1px solid #e0e0e0; background: white; }
QPushButton { background: #2563eb; color: white; padding: 6px 12px; border-radius: 4px; }
QPushButton:hover { background: #1d4ed8; }
QPushButton:pressed { background: #1e40af; }
QLineEdit { padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; }
QComboBox { padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; min-width: 150px; }
"""


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(QSS)
    app.setFont(QFont('Segoe UI', 10))

    api = ApiClient()
    win = MainWindow(api)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
