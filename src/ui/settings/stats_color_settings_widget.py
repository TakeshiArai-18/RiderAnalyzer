"""
統計カラー設定タブ
"""
from PyQt5.QtWidgets import QLabel, QGridLayout, QVBoxLayout, QCheckBox
from ui.settings.base_settings_widget import BaseSettingsWidget
from ui.widgets.color_button import ColorButton

class StatsColorSettingsWidget(BaseSettingsWidget):
    """統計カラー設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
        layout = QGridLayout()

        # タイム統計の色設定
        layout.addWidget(QLabel("タイム統計の色設定"), 0, 0, 1, 2)
        
        self.time_stats_enabled = QCheckBox("タイム統計の色付けを有効化")
        layout.addWidget(self.time_stats_enabled, 1, 0, 1, 2)
        
        self.fastest_color_button = ColorButton("最速タイム")
        layout.addWidget(QLabel("最速タイム:"), 2, 0)
        layout.addWidget(self.fastest_color_button, 2, 1)
        
        self.slowest_color_button = ColorButton("最遅タイム")
        layout.addWidget(QLabel("最遅タイム:"), 3, 0)
        layout.addWidget(self.slowest_color_button, 3, 1)

        # 標準偏差の色設定
        layout.addWidget(QLabel("標準偏差の色設定"), 4, 0, 1, 2)
        
        self.std_stats_enabled = QCheckBox("標準偏差の色付けを有効化")
        layout.addWidget(self.std_stats_enabled, 5, 0, 1, 2)
        
        self.highest_std_color_button = ColorButton("最大バラつき")
        layout.addWidget(QLabel("最大バラつき:"), 6, 0)
        layout.addWidget(self.highest_std_color_button, 6, 1)
        
        self.lowest_std_color_button = ColorButton("最小バラつき")
        layout.addWidget(QLabel("最小バラつき:"), 7, 0)
        layout.addWidget(self.lowest_std_color_button, 7, 1)

        layout.setRowStretch(8, 1)
        
        # 現在の設定を読み込む
        self._load_current_settings()
        
        # レイアウトを設定
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    def _load_current_settings(self):
        """現在の設定を読み込む"""
        settings = self.config_manager.config.get('stats_table_settings', {})
        
        # タイム統計の設定
        time_stats = settings.get('time_stats', {})
        self.time_stats_enabled.setChecked(time_stats.get('enabled', True))
        self.fastest_color_button.set_color(time_stats.get('fastest', '#C8FFC8'))
        self.slowest_color_button.set_color(time_stats.get('slowest', '#FFC8C8'))
        
        # 標準偏差の設定
        std_dev_stats = settings.get('std_dev_stats', {})
        self.std_stats_enabled.setChecked(std_dev_stats.get('enabled', True))
        self.highest_std_color_button.set_color(std_dev_stats.get('highest', '#FFE8C8'))
        self.lowest_std_color_button.set_color(std_dev_stats.get('lowest', '#C8E8FF'))
    
    def save_settings(self):
        """統計カラー設定を保存"""
        stats_color_settings = {
            'time_stats': {
                'enabled': self.time_stats_enabled.isChecked(),
                'fastest': self.fastest_color_button.get_color(),
                'slowest': self.slowest_color_button.get_color()
            },
            'std_dev_stats': {
                'enabled': self.std_stats_enabled.isChecked(),
                'highest': self.highest_std_color_button.get_color(),
                'lowest': self.lowest_std_color_button.get_color()
            }
        }
        self.config_manager.update_setting("stats_table_settings", "settings", stats_color_settings)
