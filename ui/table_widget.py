from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class TableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Lap', 'Time', 'Sector 1', 'Sector 2', 'Sector 3'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_data(self, data, analysis_results):
        self.table.setRowCount(len(data))
        fastest_lap = analysis_results.get('fastest_lap')
        slowest_lap = analysis_results.get('slowest_lap')
        fastest_sectors = analysis_results.get('fastest_sectors', {})
        slowest_sectors = analysis_results.get('slowest_sectors', {})

        for row, lap_data in enumerate(data):
            lap_number = QTableWidgetItem(str(lap_data['lap']))
            lap_time = QTableWidgetItem(lap_data['time'])
            sector1 = QTableWidgetItem(lap_data['sector1'])
            sector2 = QTableWidgetItem(lap_data['sector2'])
            sector3 = QTableWidgetItem(lap_data['sector3'])

            items = [lap_number, lap_time, sector1, sector2, sector3]
            for col, item in enumerate(items):
                self.table.setItem(row, col, item)
                item.setTextAlignment(Qt.AlignCenter)

            if lap_data['lap'] == fastest_lap:
                self._set_row_color(row, QColor(144, 238, 144))  # Light green
            elif lap_data['lap'] == slowest_lap:
                self._set_row_color(row, QColor(255, 182, 193))  # Light red

            self._highlight_sectors(row, lap_data, fastest_sectors, slowest_sectors)

    def _set_row_color(self, row, color):
        for col in range(self.table.columnCount()):
            self.table.item(row, col).setBackground(color)

    def _highlight_sectors(self, row, lap_data, fastest_sectors, slowest_sectors):
        sector_cols = {'sector1': 2, 'sector2': 3, 'sector3': 4}
        
        for sector, col in sector_cols.items():
            if lap_data[sector] == fastest_sectors.get(sector):
                self.table.item(row, col).setBackground(QColor(144, 238, 144))
            elif lap_data[sector] == slowest_sectors.get(sector):
                self.table.item(row, col).setBackground(QColor(255, 182, 193))

    def clear_table(self):
        self.table.setRowCount(0)