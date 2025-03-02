from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from utils.time_converter import TimeConverter
from utils.export_utils import StatsExporter
from ui.table_items import TimeStatItem, StdDevStatItem

class StatsTableWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.time_converter = TimeConverter()
        self.stats_exporter = StatsExporter()
        self.current_stats = {}  # 現在表示中の統計データ
        self.headers = [
            "Rider",
            "Lap Time", "Lap Time SD",
            "Sector1", "Sector1 SD",
            "Sector2", "Sector2 SD",
            "Sector3", "Sector3 SD"
        ]
        self.setup_ui()

    def setup_ui(self):
        """UIの初期設定"""
        # メインレイアウト
        layout = QVBoxLayout(self)
        
        # ボタン用のレイアウト
        button_layout = QHBoxLayout()
        
        # エクスポートボタン
        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_csv_button)
        
        export_md_button = QPushButton("Export Markdown")
        export_md_button.clicked.connect(self.export_to_markdown)
        button_layout.addWidget(export_md_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # テーブルの作成と設定
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        # ヘッダーの設定
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Rider列
        for i in range(1, len(self.headers)):
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            self.table.setColumnWidth(i, 100)  # 時間データ用の列幅

        # その他の設定
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

    def _find_extreme_values(self, stats_data):
        """最速/最遅タイムと最大/最小標準偏差を特定"""
        extremes = {
            'times': {
                'lap_time': {'min': float('inf'), 'max': float('-inf')},
                'sector1': {'min': float('inf'), 'max': float('-inf')},
                'sector2': {'min': float('inf'), 'max': float('-inf')},
                'sector3': {'min': float('inf'), 'max': float('-inf')}
            },
            'std_devs': {
                'lap_time': {'min': float('inf'), 'max': float('-inf')},
                'sector1': {'min': float('inf'), 'max': float('-inf')},
                'sector2': {'min': float('inf'), 'max': float('-inf')},
                'sector3': {'min': float('inf'), 'max': float('-inf')}
            }
        }

        # 全ての値をスキャンして最大/最小を特定
        for stats in stats_data.values():
            # ラップタイム
            lap_time = stats['lap_time']['moving_avg']
            lap_std = stats['lap_time']['std_dev']
            if lap_time > 0:
                extremes['times']['lap_time']['min'] = min(extremes['times']['lap_time']['min'], lap_time)
                extremes['times']['lap_time']['max'] = max(extremes['times']['lap_time']['max'], lap_time)
            if lap_std > 0:
                extremes['std_devs']['lap_time']['min'] = min(extremes['std_devs']['lap_time']['min'], lap_std)
                extremes['std_devs']['lap_time']['max'] = max(extremes['std_devs']['lap_time']['max'], lap_std)

            # セクタータイム
            for sector in ['sector1', 'sector2', 'sector3']:
                sector_time = stats['sectors'][sector]['moving_avg']
                sector_std = stats['sectors'][sector]['std_dev']
                if sector_time > 0:
                    extremes['times'][sector]['min'] = min(extremes['times'][sector]['min'], sector_time)
                    extremes['times'][sector]['max'] = max(extremes['times'][sector]['max'], sector_time)
                if sector_std > 0:
                    extremes['std_devs'][sector]['min'] = min(extremes['std_devs'][sector]['min'], sector_std)
                    extremes['std_devs'][sector]['max'] = max(extremes['std_devs'][sector]['max'], sector_std)

        return extremes

    def _apply_color_to_cell(self, item, value, extremes, type_key, field_key, settings):
        """セルに色を適用"""
        if not settings['enabled'] or value == 0:
            return

        if isinstance(item, TimeStatItem):
            if value == extremes['times'][field_key]['min']:
                item.setBackground(QColor(settings['fastest']))
            elif value == extremes['times'][field_key]['max']:
                item.setBackground(QColor(settings['slowest']))
        elif isinstance(item, StdDevStatItem):
            if value == extremes['std_devs'][field_key]['min']:
                item.setBackground(QColor(settings['lowest']))
            elif value == extremes['std_devs'][field_key]['max']:
                item.setBackground(QColor(settings['highest']))

    def update_statistics(self, stats_data):
        """統計情報でテーブルを更新"""
        try:
            self.current_stats = stats_data  # 統計データを保存
            self.table.setSortingEnabled(False)  # ソートを一時的に無効化
            self.table.setRowCount(0)  # テーブルをクリア

            if not stats_data:
                return

            # 最大/最小値を特定
            extremes = self._find_extreme_values(stats_data)
            
            # 設定を取得
            settings = self.config_manager.config.get('stats_table_settings', {})
            time_settings = settings.get('time_stats', {})
            std_settings = settings.get('std_dev_stats', {})

            for rider, stats in stats_data.items():
                row = self.table.rowCount()
                self.table.insertRow(row)

                # ライダー名
                self.table.setItem(row, 0, QTableWidgetItem(rider))

                # ラップタイム統計
                lap_stats = stats['lap_time']
                lap_time_item = TimeStatItem(lap_stats['moving_avg'])
                lap_std_item = StdDevStatItem(lap_stats['std_dev'])
                
                self.table.setItem(row, 1, lap_time_item)
                self.table.setItem(row, 2, lap_std_item)
                
                self._apply_color_to_cell(lap_time_item, lap_stats['moving_avg'], 
                                        extremes, 'times', 'lap_time', time_settings)
                self._apply_color_to_cell(lap_std_item, lap_stats['std_dev'], 
                                        extremes, 'std_devs', 'lap_time', std_settings)

                # セクター統計
                for i, sector in enumerate(['sector1', 'sector2', 'sector3']):
                    sector_stats = stats['sectors'][sector]
                    col_offset = 3 + i * 2
                    
                    time_item = TimeStatItem(sector_stats['moving_avg'])
                    std_item = StdDevStatItem(sector_stats['std_dev'])
                    
                    self.table.setItem(row, col_offset, time_item)
                    self.table.setItem(row, col_offset + 1, std_item)
                    
                    self._apply_color_to_cell(time_item, sector_stats['moving_avg'], 
                                            extremes, 'times', sector, time_settings)
                    self._apply_color_to_cell(std_item, sector_stats['std_dev'], 
                                            extremes, 'std_devs', sector, std_settings)

            self.table.setSortingEnabled(True)  # ソートを再有効化

        except Exception as e:
            print(f"Error updating statistics table: {str(e)}")

    def export_to_csv(self):
        """統計データをCSVファイルにエクスポート"""
        if not self.current_stats:
            QMessageBox.warning(self, "Warning", "No data to export")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        if filepath:
            if self.stats_exporter.export_to_csv(self.current_stats, filepath):
                QMessageBox.information(self, "Success", "Data exported successfully")
            else:
                QMessageBox.critical(self, "Error", "Failed to export data")

    def export_to_markdown(self):
        """統計データをMarkdownファイルにエクスポート"""
        if not self.current_stats:
            QMessageBox.warning(self, "Warning", "No data to export")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown", "", "Markdown Files (*.md)"
        )
        if filepath:
            if self.stats_exporter.export_to_markdown(self.current_stats, filepath):
                QMessageBox.information(self, "Success", "Data exported successfully")
            else:
                QMessageBox.critical(self, "Error", "Failed to export data")
