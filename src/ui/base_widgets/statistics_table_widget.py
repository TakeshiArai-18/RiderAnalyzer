"""
Statistics Table Widget Module
統計データ表示用のテーブルウィジェットを提供します。
"""
from PyQt5.QtWidgets import (QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QTableWidgetItem)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd

from ui.base_widgets.base_table_widget import BaseTableWidget, TableColorUtils
from ui.table_items import TimeStatItem, StdDevStatItem
from utils.time_converter import TimeConverter
from utils.export_utils import StatsExporter


class StatisticsTableWidget(BaseTableWidget):
    """統計データ表示用テーブルウィジェット"""
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.time_converter = TimeConverter()
        self.stats_exporter = StatsExporter()
        self.current_stats = {}
        self.setup_export_buttons()
        self.configure_columns()
        
    def setup_export_buttons(self):
        """エクスポートボタンの設定"""
        button_layout = QHBoxLayout()
        
        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_csv_button)
        
        export_md_button = QPushButton("Export Markdown")
        export_md_button.clicked.connect(self.export_to_markdown)
        button_layout.addWidget(export_md_button)
        
        button_layout.addStretch()
        
        # BaseTableWidgetのmain_layoutの先頭に追加
        self.main_layout.insertLayout(0, button_layout)
        
    def configure_columns(self):
        """カラム設定"""
        # セクター数を取得
        num_sectors = self.config_manager.get_num_sectors() if self.config_manager else 3
        
        # ヘッダーを動的に生成
        headers = ["Rider", "Lap Time", "Lap Time SD"]
        
        # セクターごとのヘッダーを動的に追加
        for i in range(1, num_sectors + 1):
            headers.append(f"Sector{i}")
            headers.append(f"Sector{i} SD")
        
        resizable_columns = [0]  # Rider列のみリサイズ可能
        fixed_width_columns = {i: 100 for i in range(1, len(headers))}  # 残りの列は固定幅
        
        self.configure_header(headers, resizable_columns, fixed_width_columns)
        self.table.setSortingEnabled(True)  # ソート機能を有効化
    
    def update_data(self, stats, config=None):
        """統計データを更新し、テーブルに表示する
        
        Args:
            stats (dict): 統計データ
            config (dict, optional): 表示設定
        """
        self.current_stats = stats
        self.update_table(config)
    
    def update_table(self, config=None):
        """テーブルを更新する
        
        Args:
            config (dict, optional): 表示設定
        """
        self.clear_table()  # 基底クラスのメソッドを使用
        if not self.current_stats:
            return

        # 統計データをテーブルに設定
        rider_stats = self.current_stats.get('rider_stats', {})
        if not rider_stats:
            return
            
        # セクター数を取得
        num_sectors = self.config_manager.get_num_sectors() if self.config_manager else 3
        
        # テーブルの列数が変わっていれば再設定
        total_columns = 3 + num_sectors * 2  # Rider + Lap Time/SD + Sectors/SD
        if self.table.columnCount() != total_columns:
            self.configure_columns()
            
        # テーブルにデータを設定
        self.table.setRowCount(len(rider_stats))
        for row, (rider, stats) in enumerate(rider_stats.items()):
            # Rider名
            self.table.setItem(row, 0, QTableWidgetItem(rider))
            
            # ラップタイム統計
            if 'lap_time_mean' in stats:
                self.table.setItem(row, 1, TimeStatItem(stats['lap_time_mean']))
            if 'lap_time_std' in stats:
                self.table.setItem(row, 2, StdDevStatItem(stats['lap_time_std']))
                
            # セクター統計（動的に処理）
            for i in range(1, num_sectors + 1):
                # セクター統計の列位置を計算
                col_offset = 3 + (i-1) * 2
                
                # セクターの平均値
                sector_mean_key = f'sector{i}_mean'
                if sector_mean_key in stats:
                    self.table.setItem(row, col_offset, TimeStatItem(stats[sector_mean_key]))
                    
                # セクターの標準偏差
                sector_std_key = f'sector{i}_std'
                if sector_std_key in stats:
                    self.table.setItem(row, col_offset + 1, StdDevStatItem(stats[sector_std_key]))

        # 最速ライダーと最遅ライダーの行に色を付ける
        if 'fastest_rider' in self.current_stats and 'slowest_rider' in self.current_stats:
            fastest_rider = self.current_stats['fastest_rider']
            slowest_rider = self.current_stats['slowest_rider']
            
            for row in range(self.table.rowCount()):
                rider_item = self.table.item(row, 0)
                if rider_item and rider_item.text() == fastest_rider:
                    self.apply_color_to_row(row, QColor('lightgreen'))  # 基底クラスのメソッドを使用
                elif rider_item and rider_item.text() == slowest_rider:
                    self.apply_color_to_row(row, QColor('lightcoral'))  # 基底クラスのメソッドを使用
    
    def update_statistics(self, stats_data):
        """統計情報でテーブルを更新 (StatsTableWidgetとの互換性用メソッド)"""
        try:
            self.current_stats = stats_data  # 統計データを保存
            self.table.setSortingEnabled(False)  # ソートを一時的に無効化
            self.clear_table()  # テーブルをクリア

            if not stats_data:
                return
            
            # セクター数を取得
            num_sectors = self.config_manager.get_num_sectors() if self.config_manager else 3
            
            # テーブルの列数が変わっていれば再設定
            total_columns = 3 + num_sectors * 2  # Rider + Lap Time/SD + Sectors/SD
            if self.table.columnCount() != total_columns:
                self.configure_columns()

            # 特別なキーをフィルタリング
            special_keys = ['fastest_rider', 'slowest_rider']
            rider_data = {k: v for k, v in stats_data.items() if k not in special_keys}
            
            # 最速/最遅ライダーの特定
            # データから自動的に特定する
            if 'fastest_rider' not in stats_data or 'slowest_rider' not in stats_data:
                try:
                    fastest_rider = min(rider_data.keys(), key=lambda r: rider_data[r]['lap_time']['moving_avg'])
                    slowest_rider = max(rider_data.keys(), key=lambda r: rider_data[r]['lap_time']['moving_avg'])
                    self.current_stats['fastest_rider'] = fastest_rider
                    self.current_stats['slowest_rider'] = slowest_rider
                except (KeyError, ValueError):
                    pass
            
            # 最大/最小値を特定
            extremes = self._find_extreme_values(rider_data)
            
            # 設定を取得
            settings = self.config_manager.config.get('stats_table_settings', {})
            time_settings = settings.get('time_stats', {})
            std_settings = settings.get('std_dev_stats', {})

            for rider, stats in rider_data.items():
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

                # セクタータイム（動的に処理）
                for i in range(1, num_sectors + 1):
                    sector_key = f'sector{i}'
                    if sector_key in stats['sectors']:
                        sector_stats = stats['sectors'][sector_key]
                        col_offset = 3 + (i-1) * 2  # ラップタイム列(2列)の後からセクターデータが始まる
                        
                        time_item = TimeStatItem(sector_stats['moving_avg'])
                        std_item = StdDevStatItem(sector_stats['std_dev'])
                        
                        self.table.setItem(row, col_offset, time_item)
                        self.table.setItem(row, col_offset + 1, std_item)
                        
                        self._apply_color_to_cell(time_item, sector_stats['moving_avg'], 
                                                extremes, 'times', sector_key, time_settings)
                        self._apply_color_to_cell(std_item, sector_stats['std_dev'], 
                                                extremes, 'std_devs', sector_key, std_settings)

            self.table.setSortingEnabled(True)  # ソートを再有効化

        except Exception as e:
            print(f"Error updating statistics table: {str(e)}")
    
    def _find_extreme_values(self, stats_data):
        """最速/最遅タイムと最大/最小標準偏差を特定"""
        # セクター数を取得
        num_sectors = self.config_manager.get_num_sectors() if self.config_manager else 3
        
        extremes = {
            'times': {
                'lap_time': {'min': float('inf'), 'max': float('-inf')}
            },
            'std_devs': {
                'lap_time': {'min': float('inf'), 'max': float('-inf')}
            }
        }
        
        # セクターごとの極値を初期化
        for i in range(1, num_sectors + 1):
            sector_key = f'sector{i}'
            extremes['times'][sector_key] = {'min': float('inf'), 'max': float('-inf')}
            extremes['std_devs'][sector_key] = {'min': float('inf'), 'max': float('-inf')}

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

            # セクタータイム（動的に処理）
            for i in range(1, num_sectors + 1):
                sector_key = f'sector{i}'
                if sector_key in stats['sectors']:
                    sector_time = stats['sectors'][sector_key]['moving_avg']
                    sector_std = stats['sectors'][sector_key]['std_dev']
                    if sector_time > 0:
                        extremes['times'][sector_key]['min'] = min(extremes['times'][sector_key]['min'], sector_time)
                        extremes['times'][sector_key]['max'] = max(extremes['times'][sector_key]['max'], sector_time)
                    if sector_std > 0:
                        extremes['std_devs'][sector_key]['min'] = min(extremes['std_devs'][sector_key]['min'], sector_std)
                        extremes['std_devs'][sector_key]['max'] = max(extremes['std_devs'][sector_key]['max'], sector_std)

        return extremes
    
    def _apply_color_to_cell(self, item, value, extremes, type_key, field_key, settings):
        """セルに色を適用"""
        if not settings.get('enabled', False) or value == 0:
            return

        if isinstance(item, TimeStatItem):
            if value == extremes['times'][field_key]['min']:
                item.setBackground(QColor(settings.get('fastest', '#c8ffc8')))
            elif value == extremes['times'][field_key]['max']:
                item.setBackground(QColor(settings.get('slowest', '#ffc8c8')))
        elif isinstance(item, StdDevStatItem):
            if value == extremes['std_devs'][field_key]['min']:
                item.setBackground(QColor(settings.get('lowest', '#c8c8ff')))
            elif value == extremes['std_devs'][field_key]['max']:
                item.setBackground(QColor(settings.get('highest', '#ffff99')))

    def export_to_csv(self):
        """統計データをCSVファイルにエクスポート"""
        if not self.current_stats:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        if filepath:
            try:
                # テーブルデータをDataFrameに変換
                data = []
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # ヘッダー取得
                headers = []
                for col in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                
                # DataFrameを作成してCSVに保存
                df = pd.DataFrame(data, columns=headers)
                df.to_csv(filepath, index=False)
                QMessageBox.information(self, "Success", "Data exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
    
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
