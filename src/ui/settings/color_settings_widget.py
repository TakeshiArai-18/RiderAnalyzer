"""
カラー設定タブ
"""
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtCore import Qt
from ui.settings.base_settings_widget import BaseSettingsWidget
from ui.widgets.color_button import ColorButton

class ColorSettingsWidget(BaseSettingsWidget):
    """カラー設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
        widget = QGroupBox("色設定")
        layout = QVBoxLayout()
        
        # 最速ラップの色
        fastest_layout = QHBoxLayout()
        fastest_layout.addWidget(QLabel("最速ラップの色:"))
        self.fastest_lap_button = ColorButton("最速ラップ")
        fastest_color = self.config_manager.get_setting('color', 'fastest_lap') or '#00ff00'
        self.fastest_lap_button.setStyleSheet(f"background-color: {fastest_color}")
        self.fastest_lap_button.color = fastest_color
        fastest_layout.addWidget(self.fastest_lap_button)
        layout.addLayout(fastest_layout)
        
        # 最遅ラップの色
        slowest_layout = QHBoxLayout()
        slowest_layout.addWidget(QLabel("最遅ラップの色:"))
        self.slowest_lap_button = ColorButton("最遅ラップ")
        slowest_color = self.config_manager.get_setting('color', 'slowest_lap') or '#ff0000'
        self.slowest_lap_button.setStyleSheet(f"background-color: {slowest_color}")
        self.slowest_lap_button.color = slowest_color
        slowest_layout.addWidget(self.slowest_lap_button)
        layout.addLayout(slowest_layout)
        
        # 通常ラップの色
        normal_layout = QHBoxLayout()
        normal_layout.addWidget(QLabel("通常ラップの色:"))
        self.normal_lap_button = ColorButton("通常ラップ")
        normal_color = self.config_manager.get_setting('color', 'normal_lap') or '#ffffff'
        self.normal_lap_button.setStyleSheet(f"background-color: {normal_color}")
        self.normal_lap_button.color = normal_color
        normal_layout.addWidget(self.normal_lap_button)
        layout.addLayout(normal_layout)
        
        widget.setLayout(layout)
        
        # メインレイアウトをセット
        main_layout = QVBoxLayout()
        main_layout.addWidget(widget)
        self.setLayout(main_layout)
    
    def pick_color(self, button):
        """色選択ダイアログを表示して選択された色をボタンに設定"""
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}")
            button.color = color.name()
    
    def save_settings(self):
        """色設定を保存"""
        color_settings = {
            "fastest_lap": getattr(self.fastest_lap_button, 'color', '#00ff00'),
            "slowest_lap": getattr(self.slowest_lap_button, 'color', '#ff0000'),
            "normal_lap": getattr(self.normal_lap_button, 'color', '#ffffff')
        }
        self.config_manager.update_setting("color", "settings", color_settings)
