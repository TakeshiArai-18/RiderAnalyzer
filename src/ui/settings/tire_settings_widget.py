"""
タイヤ設定タブ
"""
from PyQt5.QtWidgets import QVBoxLayout
from ui.settings.base_settings_widget import BaseSettingsWidget
from ui.widgets.item_manager_widget import TireManagerWidget

class TireSettingsWidget(BaseSettingsWidget):
    """タイヤ設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
        layout = QVBoxLayout()
        
        # TireManagerWidgetを使用
        self.tire_manager = TireManagerWidget(self, self.config_manager)
        layout.addWidget(self.tire_manager)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """タイヤ設定を保存"""
        try:
            # TireManagerWidgetから情報を取得
            tires_data = self.tire_manager.get_items_dict()
            for tire_id, tire_data in tires_data.items():
                self.config_manager.update_tire(tire_id, tire_data)
        except Exception as e:
            print(f"Error saving tire settings: {e}")
