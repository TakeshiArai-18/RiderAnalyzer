"""
設定ウィジェットパッケージ
このパッケージには、設定ダイアログで使用される各タブのウィジェットが含まれています。
"""
from ui.settings.base_settings_widget import BaseSettingsWidget
from ui.settings.csv_settings_widget import CsvSettingsWidget
from ui.settings.graph_settings_widget import GraphSettingsWidget
from ui.settings.color_settings_widget import ColorSettingsWidget
from ui.settings.session_settings_widget import SessionSettingsWidget
from ui.settings.stats_color_settings_widget import StatsColorSettingsWidget
from ui.settings.rider_settings_widget import RiderSettingsWidget
from ui.settings.tire_settings_widget import TireSettingsWidget

__all__ = [
    'BaseSettingsWidget',
    'CsvSettingsWidget',
    'GraphSettingsWidget',
    'ColorSettingsWidget',
    'SessionSettingsWidget',
    'StatsColorSettingsWidget',
    'RiderSettingsWidget',
    'TireSettingsWidget'
]
