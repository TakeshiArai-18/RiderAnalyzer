"""
セッション設定タブ
"""
from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QGroupBox, QLineEdit, 
                            QHBoxLayout, QComboBox, QDoubleSpinBox)
from ui.settings.base_settings_widget import BaseSettingsWidget

class SessionSettingsWidget(BaseSettingsWidget):
    """セッション設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
        layout = QVBoxLayout()
        
        # セッション情報
        session_group = QGroupBox("セッション情報")
        session_layout = QVBoxLayout()
        
        # 現在のセッション設定を取得
        current_session = self.config_manager.get_setting("session", "settings")
        
        # セッション名
        session_name_layout = QHBoxLayout()
        session_name_layout.addWidget(QLabel("セッション名:"))
        self.session_name = QLineEdit()
        if current_session and isinstance(current_session, dict):
            self.session_name.setText(current_session.get("session", {}).get("name", ""))
        session_name_layout.addWidget(self.session_name)
        session_layout.addLayout(session_name_layout)
        
        # サーキット名
        circuit_layout = QHBoxLayout()
        circuit_layout.addWidget(QLabel("サーキット:"))
        self.circuit_name = QLineEdit()
        if current_session and isinstance(current_session, dict):
            self.circuit_name.setText(current_session.get("track", ""))
        circuit_layout.addWidget(self.circuit_name)
        session_layout.addLayout(circuit_layout)
        
        # 日付
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日付:"))
        self.session_date = QLineEdit()
        self.session_date.setPlaceholderText("YYYY-MM-DD")
        if current_session and isinstance(current_session, dict):
            self.session_date.setText(current_session.get("date", ""))
        date_layout.addWidget(self.session_date)
        session_layout.addLayout(date_layout)
        
        # セッションタイプ
        session_type_layout = QHBoxLayout()
        session_type_layout.addWidget(QLabel("セッションタイプ:"))
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems(["Practice", "Qualifying", "Race", "Test"])
        if current_session and isinstance(current_session, dict):
            current_type = current_session.get("session_type", "Practice")
            if current_type:
                self.session_type_combo.setCurrentText(current_type)
        session_type_layout.addWidget(self.session_type_combo)
        session_layout.addLayout(session_type_layout)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # コンディション情報
        condition_group = QGroupBox("コンディション")
        condition_layout = QVBoxLayout()
        
        # 天候
        weather_layout = QHBoxLayout()
        weather_layout.addWidget(QLabel("天候:"))
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["Dry", "Wet", "Half Wet"])
        if current_session and isinstance(current_session, dict):
            current_weather = current_session.get("conditions", {}).get("weather", "")
            if current_weather:
                self.weather_combo.setCurrentText(current_weather)
        weather_layout.addWidget(self.weather_combo)
        condition_layout.addLayout(weather_layout)
        
        # 気温
        air_temp_layout = QHBoxLayout()
        air_temp_layout.addWidget(QLabel("気温:"))
        self.air_temp = QDoubleSpinBox()
        self.air_temp.setRange(-20, 50)
        self.air_temp.setSuffix("°C")
        if current_session and isinstance(current_session, dict):
            air_temp = current_session.get("conditions", {}).get("air_temp", 20)
            self.air_temp.setValue(float(air_temp))
        air_temp_layout.addWidget(self.air_temp)
        condition_layout.addLayout(air_temp_layout)
        
        # トラック温度
        track_temp_layout = QHBoxLayout()
        track_temp_layout.addWidget(QLabel("トラック温度:"))
        self.track_temp = QDoubleSpinBox()
        self.track_temp.setRange(0, 100)
        self.track_temp.setSuffix("°C")
        if current_session and isinstance(current_session, dict):
            track_temp = current_session.get("conditions", {}).get("track_temp", 30)
            self.track_temp.setValue(float(track_temp))
        track_temp_layout.addWidget(self.track_temp)
        condition_layout.addLayout(track_temp_layout)
        
        condition_group.setLayout(condition_layout)
        layout.addWidget(condition_group)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """セッション設定を保存"""
        # トラック名に値がないかチェック
        circuit_name = self.circuit_name.text()
        if not circuit_name or circuit_name.strip() == "":
            circuit_name = "Unknown Track"

        # 日付に値がないかチェック
        session_date = self.session_date.text()
        if not session_date or session_date.strip() == "":
            session_date = ""

        session_settings = {
            "session": {
                "name": self.session_name.text() or "Default Session"
            },
            "track": circuit_name,
            "date": session_date,
            "session_type": self.session_type_combo.currentText() or "Practice",
            "conditions": {
                "weather": self.weather_combo.currentText(),
                "air_temp": self.air_temp.value(),
                "track_temp": self.track_temp.value()
            }
        }
        
        print(f"Debug - SessionSettingsWidget - Saving session settings: {session_settings}")
        print(f"Debug - SessionSettingsWidget - track: '{circuit_name}', date: '{session_date}'")
        self.config_manager.update_setting("session", "settings", session_settings)
        
        # 設定が正しく保存されたか確認
        saved_settings = self.config_manager.get_setting("session", "settings")
        print(f"Debug - SessionSettingsWidget - Saved settings: {saved_settings}")
