"""
テーブルウィジェットのユニットテスト

新しいテーブルウィジェットが既存のテーブルウィジェットと同様に動作することを確認します。
"""
import os
import sys
import unittest
import pandas as pd
from unittest.mock import MagicMock, patch

# PyQt5をインポート
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtCore import Qt

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ui.table_widget import TableWidget
from src.ui.stats_table_widget import StatsTableWidget
from src.ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from src.ui.base_widgets.statistics_table_widget import StatisticsTableWidget


# QApplicationのインスタンスを作成（PyQt5のウィジェットテストに必要）
app = QApplication([])


class MockConfigManager:
    """テスト用の設定マネージャーモック"""
    def __init__(self):
        self.config = {
            'stats_table_settings': {
                'time_stats': {
                    'enabled': True,
                    'fastest': '#c8ffc8',  # 薄い緑
                    'slowest': '#ffc8c8'   # 薄い赤
                },
                'std_dev_stats': {
                    'enabled': True,
                    'lowest': '#c8c8ff',   # 薄い青
                    'highest': '#ffff99'   # 薄い黄
                }
            }
        }


class TestTableWidgets(unittest.TestCase):
    """テーブルウィジェットのテストケース"""
    
    def setUp(self):
        """各テストの前に実行される"""
        # モックデータの準備
        self.lap_data = [
            {'Rider': 'Rider1', 'Lap': 1, 'LapTime': 95.123, 'Sector1': 30.1, 'Sector2': 40.2, 'Sector3': 24.823},
            {'Rider': 'Rider1', 'Lap': 2, 'LapTime': 94.567, 'Sector1': 29.8, 'Sector2': 40.0, 'Sector3': 24.767},
            {'Rider': 'Rider2', 'Lap': 1, 'LapTime': 96.789, 'Sector1': 30.5, 'Sector2': 41.1, 'Sector3': 25.189},
            {'Rider': 'Rider2', 'Lap': 2, 'LapTime': 95.432, 'Sector1': 30.2, 'Sector2': 40.5, 'Sector3': 24.732},
        ]
        
        # 分析結果のモック
        self.analysis_results = {
            'rider_stats': {
                'Rider1': {
                    'best_lap': self.lap_data[1],
                    'worst_lap': self.lap_data[0],
                    'laps': [self.lap_data[0], self.lap_data[1]]
                },
                'Rider2': {
                    'best_lap': self.lap_data[3],
                    'worst_lap': self.lap_data[2],
                    'laps': [self.lap_data[2], self.lap_data[3]]
                }
            },
            'fastest_lap': self.lap_data[1],
            'slowest_lap': self.lap_data[2]
        }
        
        # 統計データのモック
        self.stats_data = {
            'Rider1': {
                'lap_time': {
                    'moving_avg': 94.845,
                    'std_dev': 0.393
                },
                'sectors': {
                    'sector1': {
                        'moving_avg': 29.95,
                        'std_dev': 0.212
                    },
                    'sector2': {
                        'moving_avg': 40.1,
                        'std_dev': 0.141
                    },
                    'sector3': {
                        'moving_avg': 24.795,
                        'std_dev': 0.040
                    }
                }
            },
            'Rider2': {
                'lap_time': {
                    'moving_avg': 96.111,
                    'std_dev': 0.959
                },
                'sectors': {
                    'sector1': {
                        'moving_avg': 30.35,
                        'std_dev': 0.212
                    },
                    'sector2': {
                        'moving_avg': 40.8,
                        'std_dev': 0.424
                    },
                    'sector3': {
                        'moving_avg': 24.961,
                        'std_dev': 0.323
                    }
                }
            }
        }
        
        # ウィジェットのインスタンス化
        self.config_manager = MockConfigManager()
        self.old_table = TableWidget()
        self.new_table = LapDataTableWidget()
        self.old_stats_table = StatsTableWidget(self.config_manager)
        self.new_stats_table = StatisticsTableWidget(self.config_manager)
        
    def test_table_widget_row_count(self):
        """テーブルウィジェットの行数が正しいかテスト"""
        # データを更新
        self.old_table.update_data(self.lap_data, self.analysis_results)
        self.new_table.update_data(self.lap_data, self.analysis_results)
        
        # 行数が一致することを確認
        self.assertEqual(self.old_table.table.rowCount(), 4)
        self.assertEqual(self.new_table.table.rowCount(), 4)
        
    def test_table_widget_column_count(self):
        """テーブルウィジェットの列数が正しいかテスト"""
        # 列数が一致することを確認
        self.assertEqual(self.old_table.table.columnCount(), self.new_table.table.columnCount())
        
    def test_stats_table_widget_row_count(self):
        """統計テーブルウィジェットの行数が正しいかテスト"""
        # データを更新
        self.old_stats_table.update_statistics(self.stats_data)
        self.new_stats_table.update_statistics(self.stats_data)
        
        # 行数が一致することを確認
        self.assertEqual(self.old_stats_table.table.rowCount(), 2)
        self.assertEqual(self.new_stats_table.table.rowCount(), 2)
        
    def test_stats_table_widget_column_count(self):
        """統計テーブルウィジェットの列数が正しいかテスト"""
        # 列数が一致することを確認
        self.assertEqual(self.old_stats_table.table.columnCount(), self.new_stats_table.table.columnCount())
        
    def test_table_data_content(self):
        """テーブルの内容が正しいかテスト"""
        # データを更新
        self.old_table.update_data(self.lap_data, self.analysis_results)
        self.new_table.update_data(self.lap_data, self.analysis_results)
        
        # テーブルの内容をチェック
        for row in range(self.old_table.table.rowCount()):
            for col in range(self.old_table.table.columnCount()):
                old_item = self.old_table.table.item(row, col)
                new_item = self.new_table.table.item(row, col)
                
                if old_item and new_item:
                    self.assertEqual(old_item.text(), new_item.text())
                    
    def test_rider_filter(self):
        """ライダーフィルタが正しく動作するかテスト"""
        # データを更新
        self.old_table.update_data(self.lap_data, self.analysis_results)
        self.new_table.update_data(self.lap_data, self.analysis_results)
        
        # ライダーフィルタを適用
        self.old_table.on_rider_selected('Rider1')
        self.new_table.update_rider_filter('Rider1')
        
        # 表示されている行数を確認
        visible_old_rows = 0
        visible_new_rows = 0
        
        for row in range(self.old_table.table.rowCount()):
            if not self.old_table.table.isRowHidden(row):
                visible_old_rows += 1
                
        for row in range(self.new_table.table.rowCount()):
            if not self.new_table.table.isRowHidden(row):
                visible_new_rows += 1
                
        # ライダー1のデータだけが表示されていることを確認（2行）
        self.assertEqual(visible_old_rows, 2)
        self.assertEqual(visible_new_rows, 2)


if __name__ == '__main__':
    unittest.main()
