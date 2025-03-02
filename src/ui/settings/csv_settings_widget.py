"""
CSVインポート設定タブ
"""
from PyQt5.QtWidgets import QLineEdit, QLabel, QVBoxLayout, QGroupBox
from ui.settings.base_settings_widget import BaseSettingsWidget

class CsvSettingsWidget(BaseSettingsWidget):
    """CSVインポート設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
        widget = QGroupBox("CSVカラム設定")
        layout = QVBoxLayout()
        
        # 現在の設定値を取得
        lap_time_value = self.config_manager.get_setting("csv_columns", "lap_time") or "LapTime"
        sector1_value = self.config_manager.get_setting("csv_columns", "sector1") or "Sector1"
        sector2_value = self.config_manager.get_setting("csv_columns", "sector2") or "Sector2"
        sector3_value = self.config_manager.get_setting("csv_columns", "sector3") or "Sector3"
        
        self.lap_time_col = QLineEdit(lap_time_value)
        self.sector1_col = QLineEdit(sector1_value)
        self.sector2_col = QLineEdit(sector2_value)
        self.sector3_col = QLineEdit(sector3_value)
        
        # ラベルに現在の設定値を表示
        layout.addWidget(QLabel(f"ラップタイムカラム: (現在: {lap_time_value})"))
        layout.addWidget(self.lap_time_col)
        layout.addWidget(QLabel(f"セクター1カラム: (現在: {sector1_value})"))
        layout.addWidget(self.sector1_col)
        layout.addWidget(QLabel(f"セクター2カラム: (現在: {sector2_value})"))
        layout.addWidget(self.sector2_col)
        layout.addWidget(QLabel(f"セクター3カラム: (現在: {sector3_value})"))
        layout.addWidget(self.sector3_col)
        
        widget.setLayout(layout)
        
        # メインレイアウトをセット
        main_layout = QVBoxLayout()
        main_layout.addWidget(widget)
        self.setLayout(main_layout)
    
    def save_settings(self):
        """CSVカラム設定を保存"""
        csv_columns = {
            "lap_time": self.lap_time_col.text() or "LapTime",
            "sector1": self.sector1_col.text() or "Sector1",
            "sector2": self.sector2_col.text() or "Sector2",
            "sector3": self.sector3_col.text() or "Sector3"
        }
        self.config_manager.update_setting("csv", "columns", csv_columns)
