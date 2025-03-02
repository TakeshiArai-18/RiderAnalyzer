"""
設定ウィジェットの基底クラス

このモジュールは、すべての設定タブウィジェットが継承する基底クラスを定義します。
"""
from PyQt5.QtWidgets import QWidget

class BaseSettingsWidget(QWidget):
    """設定タブの基底クラス"""
    
    def __init__(self, config_manager, parent=None):
        """初期化"""
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        
    def setup_ui(self):
        """UIのセットアップ - サブクラスでオーバーライド"""
        raise NotImplementedError
        
    def save_settings(self):
        """設定の保存 - サブクラスでオーバーライド"""
        raise NotImplementedError
        
    def validate(self):
        """入力値の検証 - オプション"""
        return True
