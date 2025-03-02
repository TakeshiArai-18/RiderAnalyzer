"""
設定ページ統合例

このモジュールでは、テーブルウィジェット設定を既存の設定ページに統合する方法を示します。
実際のアプリケーションには、このファイルの内容を既存の設定ページに統合してください。
"""
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout

# 既存の設定ページコンポーネント（実際のコードに合わせて変更してください）
# from ui.settings.general_settings import GeneralSettingsWidget
# from ui.settings.display_settings import DisplaySettingsWidget

# 新しいテーブルウィジェット設定
from ui.settings.table_widget_settings import TableWidgetSettingsWidget


class SettingsDialog(QWidget):
    """設定ダイアログの例"""
    
    def __init__(self, parent=None):
        """初期化"""
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # タブウィジェット
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 一般設定タブ
        # general_settings = GeneralSettingsWidget()
        # tab_widget.addTab(general_settings, "一般")
        
        # 表示設定タブ
        # display_settings = DisplaySettingsWidget()
        # tab_widget.addTab(display_settings, "表示")
        
        # テーブルウィジェット設定タブ
        table_widget_settings = TableWidgetSettingsWidget()
        tab_widget.addTab(table_widget_settings, "テーブル")
        
        # サイズの設定
        self.setWindowTitle("設定")
        self.resize(500, 400)


# 既存のアプリケーションにテーブルウィジェット設定を追加する方法
"""
# 既存の設定ダイアログクラスの __init__ メソッドや初期化メソッド内に以下を追加:

from ui.settings.table_widget_settings import TableWidgetSettingsWidget

# テーブルウィジェット設定タブを追加
table_widget_settings = TableWidgetSettingsWidget()
self.tab_widget.addTab(table_widget_settings, "テーブル")

# 設定変更時のイベントを接続
table_widget_settings.settings_changed.connect(self.on_settings_changed)

def on_settings_changed(self):
    # 設定変更時の処理
    # 必要に応じてアプリケーションの再起動を促すなど
    QMessageBox.information(
        self,
        "設定の変更",
        "テーブルウィジェットの設定が変更されました。\n変更を反映するにはアプリケーションを再起動してください。"
    )
"""
