from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                 QTableWidget, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import pyqtSignal

class DataInputWidget(QWidget):
    data_loaded = pyqtSignal(object)

    def __init__(self, data_loader):
        super().__init__()
        self.data_loader = data_loader
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.json_button = QPushButton('Load JSON')
        self.csv_button = QPushButton('Load CSV')
        self.json_button.clicked.connect(self.load_json)
        self.csv_button.clicked.connect(self.load_csv)

        button_layout.addWidget(self.json_button)
        button_layout.addWidget(self.csv_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Lap', 'Time', 'Sector 1', 'Sector 2'])

        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON', '', 'JSON files (*.json)')
        if file_path:
            data = self.data_loader.load_json(file_path)
            self.update_table(data)
            self.data_loaded.emit(data)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV files (*.csv)')
        if file_path:
            data = self.data_loader.load_csv(file_path)
            self.update_table(data)
            self.data_loaded.emit(data)

    def update_table(self, data):
        self.table.setRowCount(len(data))
        for row, lap_data in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(lap_data['lap'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(lap_data['time'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(lap_data['sector1'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(lap_data['sector2'])))