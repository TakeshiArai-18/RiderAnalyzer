from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QLabel, QHBoxLayout)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd

class TableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout()

        # ライダー選択
        rider_layout = QHBoxLayout()
        rider_label = QLabel('Rider:')
        self.rider_combo = QComboBox()
        self.rider_combo.currentTextChanged.connect(self.on_rider_selected)
        rider_layout.addWidget(rider_label)
        rider_layout.addWidget(self.rider_combo)
        rider_layout.addStretch()
        layout.addLayout(rider_layout)

        # テーブルウィジェット
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # コンディション情報を分割するため列数増加
        self.table.setHorizontalHeaderLabels([
            'Rider', 'Lap', 'Time', 'Sector1', 'Sector2', 'Sector3', 'タイヤ', '天候', '路面温度'
        ])

        # カラムの設定
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Rider
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Lap
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Sector1
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Sector2
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Sector3
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # タイヤ
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 天候
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # 路面温度

        layout.addWidget(self.table)
        self.setLayout(layout)

        # データ保存用
        self.lap_data = []
        self.analysis_results = None

    def update_data(self, laps, analysis_results=None):
        """データを更新し、テーブルに表示する"""
        self.lap_data = laps
        self.analysis_results = analysis_results

        # ライダーリストを更新
        self.update_rider_list()

        # テーブルを更新
        self.update_table()

    def update_rider_list(self):
        """ライダーリストを更新する"""
        self.rider_combo.clear()
        if not self.lap_data:
            return

        riders = sorted(set(lap['Rider'] for lap in self.lap_data))
        self.rider_combo.addItem('All Riders')
        self.rider_combo.addItems(riders)

    def update_table(self):
        """テーブルを更新する"""
        self.table.setRowCount(0)
        if not self.lap_data:
            return

        # 選択されているライダー
        selected_rider = self.rider_combo.currentText()

        # 表示するラップデータをフィルタリング
        display_laps = self.lap_data
        if selected_rider != 'All Riders':
            display_laps = [lap for lap in self.lap_data if lap['Rider'] == selected_rider]

        # テーブルにデータを設定
        self.table.setRowCount(len(display_laps))
        for row, lap in enumerate(display_laps):
            # 基本データの設定
            self.table.setItem(row, 0, QTableWidgetItem(str(lap['Rider'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(lap['Lap'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(lap['LapTime'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(lap['Sector1'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(lap['Sector2'])))
            self.table.setItem(row, 5, QTableWidgetItem(str(lap['Sector3'])))

            # コンディション情報を個別に設定
            self.table.setItem(row, 6, QTableWidgetItem(str(lap.get('TireType', ''))))
            self.table.setItem(row, 7, QTableWidgetItem(str(lap.get('Weather', ''))))
            self.table.setItem(row, 8, QTableWidgetItem(str(lap.get('TrackTemp', ''))))

            # 最速/最遅ラップの色付け
            if self.analysis_results and 'rider_stats' in self.analysis_results:
                row_color = None
                current_rider = lap['Rider']
                current_lap_time = lap['LapTime']

                # 選択されたライダーの場合は個別の最速/最遅を使用
                if selected_rider != 'All Riders' and current_rider == selected_rider:
                    rider_stats = self.analysis_results['rider_stats'].get(current_rider)
                    if rider_stats:
                        if current_lap_time == rider_stats['best_lap']['LapTime']:
                            row_color = QColor(200, 255, 200)  # 薄い緑
                        elif current_lap_time == rider_stats['worst_lap']['LapTime']:
                            row_color = QColor(255, 200, 200)  # 薄い赤
                # 全ライダー表示の場合は全体の最速/最遅を使用
                elif selected_rider == 'All Riders':
                    if current_lap_time == self.analysis_results['fastest_lap']['LapTime']:
                        row_color = QColor(200, 255, 200)  # 薄い緑
                    elif current_lap_time == self.analysis_results['slowest_lap']['LapTime']:
                        row_color = QColor(255, 200, 200)  # 薄い赤

                if row_color:
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(row_color)

    def on_rider_selected(self, rider):
        """ライダーが選択されたときの処理"""
        self.update_table()