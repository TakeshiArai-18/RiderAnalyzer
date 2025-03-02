"""
Table Widget Extension Module
既存のテーブルウィジェットクラスを拡張するモジュールです。
段階的なリファクタリングを可能にします。
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ui.table_widget import TableWidget
from ui.stats_table_widget import StatsTableWidget
from ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from ui.base_widgets.statistics_table_widget import StatisticsTableWidget


class ExtendedTableWidget(TableWidget):
    """既存のTableWidgetに新しい基底クラスの機能を拡張するクラス"""
    def __init__(self, parent=None):
        # 親クラスの初期化
        super().__init__(parent)
        
        # 新しいウィジェットの作成
        self._new_widget = LapDataTableWidget(parent)
        
        # 既存のウィジェットの初期設定を行った後に、新しいウィジェットの設定を追加
        # UIの置き換えはしないが、データ関連のメソッドをオーバーライドする
        
    def update_data(self, laps, analysis_results=None):
        """データを更新し、テーブルに表示する"""
        # 元のメソッドを呼び出し
        super().update_data(laps, analysis_results)
        
        # 新しいウィジェットにも同じデータを設定
        self._new_widget.update_data(laps, analysis_results)


class ExtendedStatsTableWidget(StatsTableWidget):
    """既存のStatsTableWidgetに新しい基底クラスの機能を拡張するクラス"""
    def __init__(self, config_manager, parent=None):
        # 親クラスの初期化
        super().__init__(config_manager, parent)
        
        # 新しいウィジェットの作成
        self._new_widget = StatisticsTableWidget(config_manager, parent)
        
        # 既存のウィジェットの初期設定を行った後に、新しいウィジェットの設定を追加
        # UIの置き換えはしないが、データ関連のメソッドをオーバーライドする
        
    def update_statistics(self, stats_data):
        """統計情報でテーブルを更新"""
        # 元のメソッドを呼び出し
        super().update_statistics(stats_data)
        
        # 新しいウィジェットにも同じデータを設定
        self._new_widget.update_statistics(stats_data)
