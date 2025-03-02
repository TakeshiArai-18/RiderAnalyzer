from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox,
                             QDoubleSpinBox, QCheckBox, QColorDialog, QGridLayout, QWidget,
                             QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from app.config_manager import ConfigManager
from ui.widgets.color_button import ColorButton
from ui.widgets.item_manager_widget import RiderManagerWidget, TireManagerWidget

# 新しい設定ウィジェットをインポート
from ui.settings.csv_settings_widget import CsvSettingsWidget
from ui.settings.graph_settings_widget import GraphSettingsWidget
from ui.settings.color_settings_widget import ColorSettingsWidget
from ui.settings.session_settings_widget import SessionSettingsWidget
from ui.settings.stats_color_settings_widget import StatsColorSettingsWidget
from ui.settings.rider_settings_widget import RiderSettingsWidget
from ui.settings.tire_settings_widget import TireSettingsWidget

class SettingsDialog(QDialog):
    settings_updated = pyqtSignal(dict)  # 設定更新シグナルを追加

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager if config_manager else parent.config_manager
        self.setWindowTitle("設定")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # タブウィジェットを作成
        self.tab_widget = QTabWidget()
        
        # 各タブを追加（新しいウィジェットクラスを使用）
        self.csv_settings = CsvSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.csv_settings, "CSVインポート")
        
        self.graph_settings = GraphSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.graph_settings, "グラフ")
        
        self.color_settings = ColorSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.color_settings, "カラー")
        
        self.session_settings = SessionSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.session_settings, "セッション")
        
        self.stats_color_settings = StatsColorSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.stats_color_settings, "統計カラー")
        
        self.rider_settings = RiderSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.rider_settings, "ライダー")
        
        self.tire_settings = TireSettingsWidget(self.config_manager, self)
        self.tab_widget.addTab(self.tire_settings, "タイヤ")
        
        layout.addWidget(self.tab_widget)
        
        # OKボタン
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_settings)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """全ての設定を保存"""
        self.csv_settings.save_settings()
        self.graph_settings.save_settings()
        self.color_settings.save_settings()
        self.session_settings.save_settings()
        self.stats_color_settings.save_settings()
        self.rider_settings.save_settings()
        self.tire_settings.save_settings()
        
        # 設定の保存と更新通知
        self.config_manager.save_config()
        self.settings_updated.emit(self.config_manager.config)
        self.accept()