"""
Table Widget Bridge Module
既存のテーブルウィジェットと新しいテーブルウィジェットの橋渡しを行います。
既存のコードを変更せずに、新しいウィジェットに移行するために使用します。
"""
from PyQt5.QtCore import pyqtSignal

# 既存のウィジェット
from ui.table_widget import TableWidget
from ui.stats_table_widget import StatsTableWidget

# 新しいウィジェット
from ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from ui.base_widgets.statistics_table_widget import StatisticsTableWidget


class BridgeTableWidget(TableWidget):
    """
    既存のTableWidgetクラスを継承し、内部では新しいLapDataTableWidgetを使用するブリッジクラス。
    既存のコードを変更せずに、新しいウィジェットに置き換えることができます。
    """
    
    def __init__(self, parent=None):
        """初期化"""
        super().__init__(parent)
        
        # 内部的に新しいウィジェットを使用
        self._new_widget = LapDataTableWidget(parent)
        
        # レイアウトに追加
        self.layout().addWidget(self._new_widget)
        
        # シグナルの接続
        self._new_widget.lap_selected.connect(self.lap_selected.emit)
        
    def update_data(self, laps, analysis=None):
        """データの更新（既存のメソッドをオーバーライド）"""
        # 既存のウィジェットの振る舞いを維持
        super().update_data(laps, analysis)
        
        # 新しいウィジェットも更新
        self._new_widget.update_data(laps, analysis)
        
    def on_rider_selected(self, rider_name):
        """ライダー選択時の処理（既存のメソッドをオーバーライド）"""
        # 既存のウィジェットの振る舞いを維持
        super().on_rider_selected(rider_name)
        
        # 新しいウィジェットにも反映
        self._new_widget.update_rider_filter(rider_name)


class BridgeStatsTableWidget(StatsTableWidget):
    """
    既存のStatsTableWidgetクラスを継承し、内部では新しいStatisticsTableWidgetを使用するブリッジクラス。
    既存のコードを変更せずに、新しいウィジェットに置き換えることができます。
    """
    
    def __init__(self, config_manager, parent=None):
        """初期化"""
        super().__init__(config_manager, parent)
        
        # 内部的に新しいウィジェットを使用
        self._new_widget = StatisticsTableWidget(config_manager, parent)
        
        # レイアウトに追加
        self.layout().addWidget(self._new_widget)
        
    def update_statistics(self, stats_data):
        """統計情報の更新（既存のメソッドをオーバーライド）"""
        # 既存のウィジェットの振る舞いを維持
        super().update_statistics(stats_data)
        
        # 新しいウィジェットも更新
        self._new_widget.update_statistics(stats_data)
        
    def export_to_csv(self, filename):
        """CSVへのエクスポート"""
        return self._new_widget.export_to_csv(filename)
        
    def export_to_markdown(self, filename):
        """Markdownへのエクスポート"""
        return self._new_widget.export_to_markdown(filename)


def get_lap_data_table_widget(parent=None):
    """ラップデータテーブルウィジェットのインスタンスを取得
    
    既存のTableWidgetクラスの代わりに使用できます。
    
    Args:
        parent: 親ウィジェット
        
    Returns:
        BridgeTableWidget: 新しいテーブルウィジェットのインスタンス
    """
    return BridgeTableWidget(parent)


def get_statistics_table_widget(config_manager, parent=None):
    """統計データテーブルウィジェットのインスタンスを取得
    
    既存のStatsTableWidgetクラスの代わりに使用できます。
    
    Args:
        config_manager: 設定マネージャーのインスタンス
        parent: 親ウィジェット
        
    Returns:
        BridgeStatsTableWidget: 新しいテーブルウィジェットのインスタンス
    """
    return BridgeStatsTableWidget(config_manager, parent)
