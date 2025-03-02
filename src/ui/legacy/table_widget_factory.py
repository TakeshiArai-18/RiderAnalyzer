"""
Table Widget Factory Module
テーブルウィジェットを生成するためのファクトリ関数を提供します。
既存のコードを変更せずに、新しいウィジェットに徐々に移行するために使用します。
"""
from typing import Optional, Callable, Union, Dict, Any

# 既存のクラス
from ui.table_widget import TableWidget
from ui.stats_table_widget import StatsTableWidget

# 新しいクラス
from ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from ui.base_widgets.statistics_table_widget import StatisticsTableWidget


def create_lap_table_widget(parent=None, use_new_implementation: bool = False) -> Union[TableWidget, LapDataTableWidget]:
    """ラップデータテーブルウィジェットを生成する
    
    Args:
        parent: 親ウィジェット
        use_new_implementation: 新しい実装を使用するかどうか（デフォルトはFalse）
        
    Returns:
        ラップデータテーブルウィジェット
    """
    if use_new_implementation:
        return LapDataTableWidget(parent=parent)
    else:
        return TableWidget(parent=parent)


def create_stats_table_widget(config_manager, parent=None, use_new_implementation: bool = False) -> Union[StatsTableWidget, StatisticsTableWidget]:
    """統計データテーブルウィジェットを生成する
    
    Args:
        config_manager: 設定マネージャー
        parent: 親ウィジェット
        use_new_implementation: 新しい実装を使用するかどうか（デフォルトはFalse）
        
    Returns:
        統計データテーブルウィジェット
    """
    if use_new_implementation:
        return StatisticsTableWidget(config_manager=config_manager, parent=parent)
    else:
        return StatsTableWidget(config_manager=config_manager, parent=parent)


# アプリケーション全体で新しい実装を使用するかどうかのフラグ
USE_NEW_TABLE_IMPLEMENTATION = False


def set_use_new_table_implementation(use_new: bool) -> None:
    """新しいテーブル実装を使用するかどうかを設定する
    
    Args:
        use_new: 新しい実装を使用する場合はTrue
    """
    global USE_NEW_TABLE_IMPLEMENTATION
    USE_NEW_TABLE_IMPLEMENTATION = use_new


def get_lap_table_widget(parent=None) -> Union[TableWidget, LapDataTableWidget]:
    """グローバル設定に基づいてラップデータテーブルウィジェットを取得する
    
    Args:
        parent: 親ウィジェット
        
    Returns:
        ラップデータテーブルウィジェット
    """
    return create_lap_table_widget(parent=parent, use_new_implementation=USE_NEW_TABLE_IMPLEMENTATION)


def get_stats_table_widget(config_manager, parent=None) -> Union[StatsTableWidget, StatisticsTableWidget]:
    """グローバル設定に基づいて統計データテーブルウィジェットを取得する
    
    Args:
        config_manager: 設定マネージャー
        parent: 親ウィジェット
        
    Returns:
        統計データテーブルウィジェット
    """
    return create_stats_table_widget(
        config_manager=config_manager, 
        parent=parent, 
        use_new_implementation=USE_NEW_TABLE_IMPLEMENTATION
    )
