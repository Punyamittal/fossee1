"""Main application window."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QMenu, QMessageBox, QFileDialog,
    QStatusBar, QToolBar, QComboBox, QFrame, QGridLayout, QApplication,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QAction

from .upload_dialog import UploadDialog
from .data_table_widget import DataTableWidget
from .chart_widget import ChartWidget


class FetchWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, api_client, dataset_id):
        super().__init__()
        self.api_client = api_client
        self.dataset_id = dataset_id

    def run(self):
        try:
            data = self.api_client.get_dataset(self.dataset_id)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class PDFWorker(QThread):
    finished = Signal(bytes)
    error = Signal(str)

    def __init__(self, api_client, dataset_id):
        super().__init__()
        self.api_client = api_client
        self.dataset_id = dataset_id

    def run(self):
        try:
            content = self.api_client.generate_pdf(self.dataset_id)
            self.finished.emit(content)
        except Exception as e:
            self.error.emit(str(e))


class SummaryTab(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout(self)
        self.cards = {}
        for i, (key, label) in enumerate([
            ('total', 'Total Count'),
            ('flowrate', 'Avg Flowrate'),
            ('pressure', 'Avg Pressure'),
            ('temp', 'Avg Temperature'),
        ]):
            frame = QFrame()
            frame.setFrameStyle(QFrame.Box)
            frame.setStyleSheet('QFrame { background: #f8fafc; padding: 12px; } QLabel { color: #1e293b; }')
            v = QVBoxLayout(frame)
            title = QLabel(label)
            title.setStyleSheet('color: #64748b; font-size: 12px;')
            v.addWidget(title)
            lbl = QLabel('—')
            lbl.setFont(QFont('Segoe UI', 18, QFont.Bold))
            lbl.setStyleSheet('color: #0f172a;')
            self.cards[key] = lbl
            v.addWidget(lbl)
            layout.addWidget(frame, i // 2, i % 2)
        self.setLayout(layout)

    def set_data(self, summary):
        if not summary:
            return
        total = summary.get('total_count')
        self.cards['total'].setText(str(total) if total is not None else '—')
        for key, attr in [('flowrate', 'avg_flowrate'), ('pressure', 'avg_pressure'), ('temp', 'avg_temperature')]:
            v = summary.get(attr)
            if v is not None and v != '':
                try:
                    self.cards[key].setText(f"{float(v):.2f}")
                except (TypeError, ValueError):
                    self.cards[key].setText(str(v))
            else:
                self.cards[key].setText('—')


class LoginDialog(QWidget):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle('Login')
        self.setMinimumWidth(300)
        from PySide6.QtWidgets import QFormLayout, QLineEdit
        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow('Username:', self.username)
        layout.addRow('Password:', self.password)
        btn = QPushButton('Login')
        btn.clicked.connect(self._login)
        layout.addRow(btn)
        self.status = QLabel('')
        layout.addRow(self.status)

    def _login(self):
        try:
            self.api_client.login(
                self.username.text().strip(),
                self.password.text().strip(),
            )
            self.status.setText('Logged in')
            self.close()
        except Exception as e:
            self.status.setText(str(e))
            QMessageBox.critical(self, 'Login Failed', str(e))


class MainWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_dataset_id = None
        self.datasets = []
        self.worker = None
        self.pdf_worker = None
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._load_history()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        self.summary_tab = SummaryTab()
        self.data_table = DataTableWidget()
        self.chart_widget = ChartWidget()

        self.tabs.addTab(self.summary_tab, 'Summary Stats')
        self.tabs.addTab(self.data_table, 'Data Table')
        self.tabs.addTab(self.chart_widget, 'Charts')
        layout.addWidget(self.tabs)

        self.statusBar().showMessage('Ready')

    def _build_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        upload_action = QAction('Upload CSV', self)
        upload_action.triggered.connect(self._upload_csv)
        file_menu.addAction(upload_action)
        self.history_menu = menubar.addMenu('View History')
        self._populate_history_menu()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)

    def _build_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.dataset_combo = QComboBox()
        self.dataset_combo.setMinimumWidth(200)
        self.dataset_combo.currentIndexChanged.connect(self._on_combo_change)
        toolbar.addWidget(QLabel('Dataset:'))
        toolbar.addWidget(self.dataset_combo)
        pdf_btn = QPushButton('Generate PDF')
        pdf_btn.clicked.connect(self._generate_pdf)
        toolbar.addWidget(pdf_btn)
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self._show_login)
        toolbar.addWidget(login_btn)

    def _load_history(self):
        try:
            self.datasets = self.api_client.get_datasets()
        except Exception:
            self.datasets = []
        self._refresh_combo()

    def _refresh_combo(self):
        self.dataset_combo.blockSignals(True)
        self.dataset_combo.clear()
        self.dataset_combo.addItem('— Select dataset —', None)
        for d in self.datasets:
            ts = d.get('upload_timestamp', '')[:10] if d.get('upload_timestamp') else ''
            label = f"{d.get('filename', '')} ({ts})"
            self.dataset_combo.addItem(label, d.get('id'))
        self.dataset_combo.blockSignals(False)
        self._populate_history_menu()

    def _populate_history_menu(self):
        self.history_menu.clear()
        for d in self.datasets:
            act = QAction(f"{d.get('filename', '')} - {d.get('upload_timestamp', '')[:16]}", self)
            did = d.get('id')
            act.triggered.connect(lambda checked, x=did: self._select_dataset(x))
            self.history_menu.addAction(act)
        if not self.datasets:
            act = QAction('(No datasets)', self)
            act.setEnabled(False)
            self.history_menu.addAction(act)

    def _select_dataset(self, dataset_id):
        self.current_dataset_id = dataset_id
        idx = self.dataset_combo.findData(dataset_id)
        if idx >= 0:
            self.dataset_combo.setCurrentIndex(idx)
        self._load_dataset()

    def _upload_csv(self):
        dlg = UploadDialog(self.api_client, self)
        dlg.exec()
        if dlg.result:
            self._load_history()
            self.current_dataset_id = dlg.result.get('dataset_id')
            self._refresh_combo()
            idx = self.dataset_combo.findData(self.current_dataset_id)
            if idx >= 0:
                self.dataset_combo.setCurrentIndex(idx)
            self._load_dataset()

    def _on_combo_change(self, idx):
        dataset_id = self.dataset_combo.itemData(idx)
        if dataset_id:
            self.current_dataset_id = dataset_id
            self._load_dataset()

    def _load_dataset(self):
        if not self.current_dataset_id:
            return
        if self.worker and self.worker.isRunning():
            self.worker.wait()
        self.statusBar().showMessage('Loading...')
        self.worker = FetchWorker(self.api_client, self.current_dataset_id)
        self.worker.finished.connect(self._on_data_loaded)
        self.worker.error.connect(self._on_load_error)
        self.worker.start()

    def _on_data_loaded(self, data):
        self.statusBar().showMessage('Loaded')
        self.data_table.set_data(data.get('equipment_list', []))
        self.chart_widget.set_data(data)
        equipment = data.get('equipment_list', [])
        summary = {
            'total_count': data.get('total_equipment_count') or len(equipment),
            'avg_flowrate': data.get('avg_flowrate'),
            'avg_pressure': data.get('avg_pressure'),
            'avg_temperature': data.get('avg_temperature'),
        }
        # Compute from equipment if dataset-level stats are missing
        if summary['avg_flowrate'] is None and equipment:
            flowrates = [float(e.get('flowrate', 0)) for e in equipment]
            summary['avg_flowrate'] = sum(flowrates) / len(flowrates) if flowrates else None
        if summary['avg_pressure'] is None and equipment:
            pressures = [float(e.get('pressure', 0)) for e in equipment]
            summary['avg_pressure'] = sum(pressures) / len(pressures) if pressures else None
        if summary['avg_temperature'] is None and equipment:
            temps = [float(e.get('temperature', 0)) for e in equipment]
            summary['avg_temperature'] = sum(temps) / len(temps) if temps else None
        self.summary_tab.set_data(summary)

    def _on_load_error(self, msg):
        self.statusBar().showMessage('Error')
        QMessageBox.critical(self, 'Load Failed', msg)

    def _generate_pdf(self):
        if not self.current_dataset_id:
            QMessageBox.warning(self, 'PDF', 'Please select a dataset first.')
            return
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save PDF', f'report_dataset_{self.current_dataset_id}.pdf', 'PDF (*.pdf)'
        )
        if not path:
            return
        if self.pdf_worker and self.pdf_worker.isRunning():
            self.pdf_worker.wait()
        self.statusBar().showMessage('Generating PDF...')
        self.pdf_worker = PDFWorker(self.api_client, self.current_dataset_id)
        self.pdf_worker.finished.connect(lambda c: self._save_pdf(c, path))
        self.pdf_worker.error.connect(self._on_pdf_error)
        self.pdf_worker.start()

    def _save_pdf(self, content, path):
        with open(path, 'wb') as f:
            f.write(content)
        self.statusBar().showMessage(f'Saved: {path}')
        QMessageBox.information(self, 'PDF', f'Saved to {path}')

    def _on_pdf_error(self, msg):
        self.statusBar().showMessage('Error')
        QMessageBox.critical(self, 'PDF Failed', msg)

    def _show_login(self):
        dlg = LoginDialog(self.api_client, self)
        dlg.show()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.wait(3000)
        if self.pdf_worker and self.pdf_worker.isRunning():
            self.pdf_worker.wait(3000)
        event.accept()
