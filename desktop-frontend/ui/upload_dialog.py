"""Upload CSV dialog."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar, QMessageBox, QLineEdit,
)
from PySide6.QtCore import Qt, QThread, Signal


class UploadWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, api_client, filepath):
        super().__init__()
        self.api_client = api_client
        self.filepath = filepath

    def run(self):
        try:
            self.progress.emit(30)
            result = self.api_client.upload_csv(self.filepath)
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class UploadDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.result = None
        self.worker = None
        self.setWindowTitle('Upload CSV')
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText('Select CSV file...')
        layout.addWidget(self.path_edit)

        btn_layout = QHBoxLayout()
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self._browse)
        upload_btn = QPushButton('Upload')
        upload_btn.clicked.connect(self._upload)
        btn_layout.addWidget(browse_btn)
        btn_layout.addWidget(upload_btn)
        layout.addLayout(btn_layout)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status = QLabel('')
        layout.addWidget(self.status)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV', '', 'CSV files (*.csv)'
        )
        if path:
            self.path_edit.setText(path)

    def _upload(self):
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, 'Error', 'Please select a CSV file.')
            return
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText('Uploading...')
        self.worker = UploadWorker(self.api_client, path)
        self.worker.finished.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.start()

    def _on_success(self, data):
        self.progress.setVisible(False)
        self.status.setText(f"Uploaded: {data.get('filename', '')} ({data.get('total_equipment_count', 0)} equipment)")
        self.result = data
        QMessageBox.information(self, 'Success', f"Uploaded successfully!\nDataset ID: {data.get('dataset_id')}")

    def _on_error(self, msg):
        self.progress.setVisible(False)
        self.status.setText('')
        QMessageBox.critical(self, 'Upload Failed', msg)

    def reject(self):
        if self.worker and self.worker.isRunning():
            self.worker.wait(3000)
        super().reject()
