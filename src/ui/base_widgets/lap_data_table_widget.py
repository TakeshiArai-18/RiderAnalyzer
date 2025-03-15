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
        self.current_rider = None
        self.analysis_data = None
        self.config_manager = parent.config_manager if hasattr(parent, 'config_manager') else None
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
        # セクター数を取得
        num_sectors = self.config_manager.get_num_sectors() if self.config_manager else 3
        
        # ヘッダーを動的に生成
        headers = ["Rider", "Lap", "Lap Time"]
        
        # セクターごとのヘッダーを動的に追加
        for i in range(1, num_sectors + 1):
            headers.append(f"Sector{i}")
        
        # 追加列
        headers.extend(["Tire", "Weather", "Track Temp"])
        
        resizable_columns = [0]  # Rider列のみリサイズ可能
        fixed_width_columns = {
            1: 50,  # Lap
            2: 100  # Lap Time
        }
        
        # セクターの列に固定幅を設定
        for i in range(3, 3 + num_sectors):
            fixed_width_columns[i] = 100
        
        # 追加列の固定幅を設定
        offset = 3 + num_sectors
        fixed_width_columns[offset] = 80      # Tire
        fixed_width_columns[offset + 1] = 80  # Weather
        fixed_width_columns[offset + 2] = 80  # Track Temp
        
        self.configure_header(headers, resizable_columns, fixed_width_columns)
    
    def update_data(self, laps, analysis_results=None):
        """ラップデータを更新"""
        self.lap_data = laps
        self.analysis_data = analysis_results
        
        # ライダーリストを更新
        self.update_rider_list(laps)
        
        # テーブルを更新
        self.update_table(laps, analysis_results)

    def update_rider_list(self, laps):
        """ライダーリストを更新する"""
        self.rider_combo.clear()
        if not laps:
            return

        riders = sorted(set(lap.get('rider_name', lap.get('Rider', '')) for lap in laps))
        self.rider_combo.addItem('All Riders')
        self.rider_combo.addItems(riders)

    def update_table(self, lap_data, analysis_data=None):
        """テーブルデータを更新"""
        try:
            self.analysis_data = analysis_data  # 分析結果を保存
            self.table.setSortingEnabled(False)  # ソートを一時的に無効化
            self.clear_table()  # テーブルをクリア

            if not lap_data:
                return
                
            # セクター数を取得
            num_sectors = self.config_manager.get_num_sectors() if self.config_manager else 3
            
            # テーブルの列数が変わっていれば再設定
            total_columns = 6 + num_sectors  # Rider + Lap + LapTime + Sectors + Tire + Weather + TrackTemp
            if self.table.columnCount() != total_columns:
                self.configure_columns()

            # 選択されたライダーでフィルタリング
            filtered_data = lap_data
            if self.current_rider and self.current_rider != "All Riders":
                filtered_data = [lap for lap in lap_data if lap.get('rider_name', lap.get('Rider', '')) == self.current_rider]

            # 最速/最遅ラップの特定（分析結果がある場合）
            fastest_lap = None
            slowest_lap = None
            
            if analysis_data:
                print(f"Debug - analysis_data keys: {analysis_data.keys()}")
                
                # 選択されたライダーの場合は個別の統計を使用
                if self.current_rider and self.current_rider != "All Riders" and 'rider_stats' in analysis_data:
                    rider_stats = analysis_data['rider_stats'].get(self.current_rider, {})
                    print(f"Debug - rider_stats for {self.current_rider}: {rider_stats.keys() if rider_stats else 'None'}")
                    
                    if rider_stats:
                        # fastest_lapキーを探す
                        if 'fastest_lap' in rider_stats:
                            fastest_lap = rider_stats['fastest_lap']
                        elif 'best_lap' in rider_stats:
                            fastest_lap = rider_stats['best_lap']
                            
                        # slowest_lapキーを探す
                        if 'slowest_lap' in rider_stats:
                            slowest_lap = rider_stats['slowest_lap']
                        elif 'worst_lap' in rider_stats:
                            slowest_lap = rider_stats['worst_lap']
                
                # 全体統計を使用
                else:
                    # 'overall_stats'キーがある場合
                    if 'overall_stats' in analysis_data:
                        overall_stats = analysis_data['overall_stats']
                        print(f"Debug - overall_stats keys: {overall_stats.keys() if overall_stats else 'None'}")
                        
                        if overall_stats:
                            # fastest_lapキーを探す
                            if 'fastest_lap' in overall_stats:
                                fastest_lap = overall_stats['fastest_lap']
                            elif 'best_lap' in overall_stats:
                                fastest_lap = overall_stats['best_lap']
                                
                            # slowest_lapキーを探す
                            if 'slowest_lap' in overall_stats:
                                slowest_lap = overall_stats['slowest_lap']
                            elif 'worst_lap' in overall_stats:
                                slowest_lap = overall_stats['worst_lap']
                    
                    # 直接ルートレベルで定義されている場合
                    else:
                        if 'fastest_lap' in analysis_data:
                            fastest_lap = analysis_data['fastest_lap']
                        elif 'best_lap' in analysis_data:
                            fastest_lap = analysis_data['best_lap']
                            
                        if 'slowest_lap' in analysis_data:
                            slowest_lap = analysis_data['slowest_lap']
                        elif 'worst_lap' in analysis_data:
                            slowest_lap = analysis_data['worst_lap']
            
            # デバッグ情報
            if fastest_lap:
                print(f"Debug - fastest_lap: {fastest_lap}")
            if slowest_lap:
                print(f"Debug - slowest_lap: {slowest_lap}")

            for lap in filtered_data:
                row = self.table.rowCount()
                self.table.insertRow(row)

                # ライダー名とラップ番号の取得
                rider_name = lap.get('rider_name', lap.get('Rider', ''))
                lap_number = lap.get('lap_number', lap.get('Lap', ''))
                
                # データ挿入
                self.table.setItem(row, 0, QTableWidgetItem(rider_name))
                self.table.setItem(row, 1, QTableWidgetItem(str(lap_number)))
                self.table.setItem(row, 2, QTableWidgetItem(lap.get('LapTime', lap.get('lap_time', ''))))

                # セクタータイム（動的に処理）
                for i in range(1, num_sectors + 1):
                    sector_key = f'sector{i}_time'
                    sector_key_old = f'Sector{i}'
                    if sector_key in lap:
                        self.table.setItem(row, 2 + i, QTableWidgetItem(lap[sector_key]))
                    elif sector_key_old in lap:
                        self.table.setItem(row, 2 + i, QTableWidgetItem(lap[sector_key_old]))

                # 追加データ
                offset = 3 + num_sectors
                self.table.setItem(row, offset, QTableWidgetItem(lap.get('TireType', lap.get('tire_type', ''))))
                self.table.setItem(row, offset + 1, QTableWidgetItem(lap.get('Weather', lap.get('weather', ''))))
                self.table.setItem(row, offset + 2, QTableWidgetItem(str(lap.get('TrackTemp', lap.get('track_temperature', '')))))

                # 最速/最遅ラップの背景色設定
                is_fastest = False
                is_slowest = False
                
                # 最速ラップのチェック
                if fastest_lap:
                    fastest_rider = fastest_lap.get('rider_name', fastest_lap.get('Rider', ''))
                    fastest_lap_num = fastest_lap.get('lap_number', fastest_lap.get('Lap', ''))
                    
                    if rider_name == fastest_rider and lap_number == fastest_lap_num:
                        is_fastest = True
                
                # 最遅ラップのチェック
                if slowest_lap:
                    slowest_rider = slowest_lap.get('rider_name', slowest_lap.get('Rider', ''))
                    slowest_lap_num = slowest_lap.get('lap_number', slowest_lap.get('Lap', ''))
                    
                    if rider_name == slowest_rider and lap_number == slowest_lap_num:
                        is_slowest = True
                
                # 背景色を設定
                if is_fastest:
                    for col in range(self.table.columnCount()):
                        self.table.item(row, col).setBackground(QColor(204, 255, 204))  # 薄緑
                elif is_slowest:
                    for col in range(self.table.columnCount()):
                        self.table.item(row, col).setBackground(QColor(255, 204, 204))  # 薄赤

            self.table.setSortingEnabled(True)  # ソートを再有効化

        except Exception as e:
            print(f"Error updating lap data table: {str(e)}")
            import traceback
            traceback.print_exc()

    def on_rider_selected(self, rider):
        """ライダー選択時の処理"""
        self.current_rider = rider
        if hasattr(self, 'update_table'):
            self.update_table(self.lap_data, self.analysis_data)
