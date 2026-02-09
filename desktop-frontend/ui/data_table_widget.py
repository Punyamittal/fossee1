"""Data table widget with sorting and search."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QLabel, QHeaderView,
)
from PySide6.QtCore import Qt


class DataTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('Search:'))
        self.search = QLineEdit()
        self.search.setPlaceholderText('Filter by name or type...')
        self.search.textChanged.connect(self._apply_filter)
        search_layout.addWidget(self.search)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def set_data(self, equipment):
        self._raw_data = equipment or []
        self._apply_filter()

    def _apply_filter(self):
        filter_text = self.search.text().lower().strip()
        if filter_text:
            data = [
                e for e in self._raw_data
                if filter_text in str(e.get('equipment_name', '')).lower()
                or filter_text in str(e.get('equipment_type', '')).lower()
            ]
        else:
            data = self._raw_data

        self.table.setRowCount(len(data))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        for i, e in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(e.get('equipment_name', ''))))
            self.table.setItem(i, 1, QTableWidgetItem(str(e.get('equipment_type', ''))))
            self.table.setItem(i, 2, QTableWidgetItem(str(e.get('flowrate', ''))))
            self.table.setItem(i, 3, QTableWidgetItem(str(e.get('pressure', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(str(e.get('temperature', ''))))
        self.table.setSortingEnabled(True)
