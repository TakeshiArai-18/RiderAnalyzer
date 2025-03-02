"""
ライダー設定タブ
"""
from PyQt5.QtWidgets import QVBoxLayout
from ui.settings.base_settings_widget import BaseSettingsWidget
from ui.widgets.item_manager_widget import RiderManagerWidget

class RiderSettingsWidget(BaseSettingsWidget):
    """ライダー設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
        layout = QVBoxLayout()
        
        # RiderManagerWidgetを使用
        self.rider_manager = RiderManagerWidget(self, self.config_manager)
        layout.addWidget(self.rider_manager)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """ライダー設定を保存"""
        try:
            # RiderManagerWidgetから情報を取得
            riders_data = self.rider_manager.get_items_dict()
            for rider_id, rider_data in riders_data.items():
                self.config_manager.update_rider(rider_id, rider_data)
        except Exception as e:
            print(f"Error saving rider settings: {e}")
