"""
Lap Data Table Widget Module
ラップデータ表示用のテーブルウィジェットを提供します。
"""
from PyQt5.QtWidgets import (QComboBox, QLabel, QHBoxLayout, QTableWidgetItem)
from PyQt5.QtGui import QColor
import pandas as pd

from ui.base_widgets.base_table_widget import BaseTableWidget, TableColorUtils


class LapDataTableWidget(BaseTableWidget):
    """ラップデータ表示用テーブルウィジェット"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lap_data = []
        self.analysis_results = None
        self.setup_rider_selector()
        self.configure_columns()
        
    def setup_rider_selector(self):
        """ライダー選択UIを設定"""
        rider_layout = QHBoxLayout()
        rider_label = QLabel('Rider:')
        self.rider_combo = QComboBox()
        self.rider_combo.currentTextChanged.connect(self.on_rider_selected)
        rider_layout.addWidget(rider_label)
        rider_layout.addWidget(self.rider_combo)
        rider_layout.addStretch()
        
        # BaseTableWidgetのmain_layoutの先頭に追加
        self.main_layout.insertLayout(0, rider_layout)
        
    def configure_columns(self):
        """カラム設定"""
        headers = ['Rider', 'Lap', 'Time', 'Sector1', 'Sector2', 'Sector3', 'タイヤ', '天候', '路面温度']
        resizable_columns = list(range(9))  # すべてのカラムをリサイズ可能に
        
        self.configure_header(headers, resizable_columns)
    
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
        self.clear_table()  # 基底クラスのメソッドを使用
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
            if self.analysis_results:  # analysis_resultsがNoneでないことを確認
                row_color = None
                current_rider = lap['Rider']
                current_lap_time = lap['LapTime']

                # 選択されたライダーの場合は個別の最速/最遅を使用
                if selected_rider != 'All Riders' and current_rider == selected_rider:
                    if 'rider_stats' in self.analysis_results:
                        rider_stats = self.analysis_results.get('rider_stats', {}).get(current_rider)
                        if rider_stats and 'best_lap' in rider_stats and 'worst_lap' in rider_stats:
                            if current_lap_time == rider_stats['best_lap']['LapTime']:
                                row_color = TableColorUtils.get_best_time_color()
                            elif current_lap_time == rider_stats['worst_lap']['LapTime']:
                                row_color = TableColorUtils.get_worst_time_color()
                # 全ライダー表示の場合は全体の最速/最遅を使用
                elif selected_rider == 'All Riders':
                    if 'fastest_lap' in self.analysis_results and 'slowest_lap' in self.analysis_results:
                        if current_lap_time == self.analysis_results['fastest_lap']['LapTime']:
                            row_color = TableColorUtils.get_best_time_color()
                        elif current_lap_time == self.analysis_results['slowest_lap']['LapTime']:
                            row_color = TableColorUtils.get_worst_time_color()

                if row_color:
                    self.apply_color_to_row(row, row_color)  # 基底クラスのメソッドを使用

    def on_rider_selected(self, rider):
        """ライダーが選択されたときの処理"""
        self.update_table()
