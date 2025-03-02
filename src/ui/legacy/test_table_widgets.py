"""
テーブルウィジェットのテストスクリプト

既存のテーブルウィジェットと新しいテーブルウィジェットの比較テストを行います。
両方のウィジェットを同時に表示して、機能の比較ができます。
"""
import sys
import random
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget

# 既存のウィジェット
from ui.table_widget import TableWidget
from ui.stats_table_widget import StatsTableWidget

# 新しいウィジェット
from ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from ui.base_widgets.statistics_table_widget import StatisticsTableWidget

# 設定マネージャーのモック
class MockConfigManager:
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


def generate_mock_lap_data(num_riders=3, laps_per_rider=5):
    """モックラップデータの生成"""
    riders = [f"Rider{i+1}" for i in range(num_riders)]
    lap_data = []
    
    for rider in riders:
        best_time = random.uniform(90.0, 120.0)  # 基準タイム
        
        for lap_num in range(1, laps_per_rider + 1):
            # 各ラップは基準タイムの周辺でランダムに変動
            lap_time = best_time + random.uniform(-5.0, 10.0)
            
            # セクタータイムもランダムに生成
            sector1 = lap_time * 0.3 + random.uniform(-1.0, 1.0)
            sector2 = lap_time * 0.4 + random.uniform(-1.0, 1.0)
            sector3 = lap_time * 0.3 + random.uniform(-1.0, 1.0)
            
            lap_data.append({
                'Rider': rider,
                'Lap': lap_num,
                'LapTime': round(lap_time, 3),
                'Sector1': round(sector1, 3),
                'Sector2': round(sector2, 3),
                'Sector3': round(sector3, 3),
                'TireType': random.choice(['Soft', 'Medium', 'Hard']),
                'Weather': random.choice(['Sunny', 'Cloudy', 'Rain']),
                'TrackTemp': random.randint(20, 40)
            })
    
    return lap_data


def generate_mock_analysis_results(lap_data):
    """モック分析結果の生成"""
    # ライダーごとに最速/最遅ラップを探す
    rider_stats = {}
    fastest_lap = None
    slowest_lap = None
    
    for lap in lap_data:
        rider = lap['Rider']
        lap_time = lap['LapTime']
        
        # 全体の最速/最遅ラップの更新
        if fastest_lap is None or lap_time < fastest_lap['LapTime']:
            fastest_lap = lap
        if slowest_lap is None or lap_time > slowest_lap['LapTime']:
            slowest_lap = lap
        
        # ライダーごとの統計情報
        if rider not in rider_stats:
            rider_stats[rider] = {
                'best_lap': lap,
                'worst_lap': lap,
                'laps': []
            }
        else:
            if lap_time < rider_stats[rider]['best_lap']['LapTime']:
                rider_stats[rider]['best_lap'] = lap
            if lap_time > rider_stats[rider]['worst_lap']['LapTime']:
                rider_stats[rider]['worst_lap'] = lap
        
        rider_stats[rider]['laps'].append(lap)
    
    return {
        'rider_stats': rider_stats,
        'fastest_lap': fastest_lap,
        'slowest_lap': slowest_lap
    }


def generate_mock_stats_data(lap_data):
    """モック統計データの生成"""
    riders = set(lap['Rider'] for lap in lap_data)
    stats_data = {}
    
    for rider in riders:
        rider_laps = [lap for lap in lap_data if lap['Rider'] == rider]
        lap_times = [lap['LapTime'] for lap in rider_laps]
        sector1_times = [lap['Sector1'] for lap in rider_laps]
        sector2_times = [lap['Sector2'] for lap in rider_laps]
        sector3_times = [lap['Sector3'] for lap in rider_laps]
        
        # 平均と標準偏差の計算
        lap_mean = sum(lap_times) / len(lap_times)
        lap_std = (sum((t - lap_mean) ** 2 for t in lap_times) / len(lap_times)) ** 0.5
        
        s1_mean = sum(sector1_times) / len(sector1_times)
        s1_std = (sum((t - s1_mean) ** 2 for t in sector1_times) / len(sector1_times)) ** 0.5
        
        s2_mean = sum(sector2_times) / len(sector2_times)
        s2_std = (sum((t - s2_mean) ** 2 for t in sector2_times) / len(sector2_times)) ** 0.5
        
        s3_mean = sum(sector3_times) / len(sector3_times)
        s3_std = (sum((t - s3_mean) ** 2 for t in sector3_times) / len(sector3_times)) ** 0.5
        
        stats_data[rider] = {
            'lap_time': {
                'moving_avg': lap_mean,
                'std_dev': lap_std
            },
            'sectors': {
                'sector1': {
                    'moving_avg': s1_mean,
                    'std_dev': s1_std
                },
                'sector2': {
                    'moving_avg': s2_mean,
                    'std_dev': s2_std
                },
                'sector3': {
                    'moving_avg': s3_mean,
                    'std_dev': s3_std
                }
            }
        }
    
    return stats_data


class TestWindow(QMainWindow):
    """テストウィンドウ"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("テーブルウィジェットテスト")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        """UIの設定"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # タブウィジェットの作成
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # ラップデータテーブルのタブ
        lap_tab = QWidget()
        lap_layout = QVBoxLayout(lap_tab)
        
        # 既存のテーブルウィジェット
        self.old_table = TableWidget()
        lap_layout.addWidget(self.old_table)
        
        # 新しいテーブルウィジェット
        self.new_table = LapDataTableWidget()
        lap_layout.addWidget(self.new_table)
        
        tab_widget.addTab(lap_tab, "ラップデータテーブル")
        
        # 統計データテーブルのタブ
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # 設定マネージャーの作成
        config_manager = MockConfigManager()
        
        # 既存の統計テーブルウィジェット
        self.old_stats_table = StatsTableWidget(config_manager)
        stats_layout.addWidget(self.old_stats_table)
        
        # 新しい統計テーブルウィジェット
        self.new_stats_table = StatisticsTableWidget(config_manager)
        stats_layout.addWidget(self.new_stats_table)
        
        tab_widget.addTab(stats_tab, "統計データテーブル")
        
        # モックデータの生成と表示
        self.load_mock_data()
        
    def load_mock_data(self):
        """モックデータを生成して表示"""
        # ラップデータの生成
        lap_data = generate_mock_lap_data(num_riders=3, laps_per_rider=5)
        analysis_results = generate_mock_analysis_results(lap_data)
        
        # ラップデータテーブルの更新
        self.old_table.update_data(lap_data, analysis_results)
        self.new_table.update_data(lap_data, analysis_results)
        
        # 統計データの生成
        stats_data = generate_mock_stats_data(lap_data)
        
        # 統計データテーブルの更新
        self.old_stats_table.update_statistics(stats_data)
        self.new_stats_table.update_statistics(stats_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
