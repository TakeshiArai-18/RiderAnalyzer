"""
テーブルウィジェット設定

このモジュールでは、テーブルウィジェットの設定を行うためのインターフェースを提供します。
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import pyqtSignal

from ui.base_widgets.table_widget_factory import (
    set_use_new_table_implementation, 
    USE_NEW_TABLE_IMPLEMENTATION
)


class TableWidgetSettingsWidget(QWidget):
    """テーブルウィジェットの設定を行うウィジェット"""
    
    # 設定変更時のシグナル
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """初期化"""
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # タイトル
        title_label = QLabel("<h2>テーブルウィジェット設定</h2>")
        layout.addWidget(title_label)
        
        # 実装選択グループ
        impl_group = QGroupBox("使用する実装")
        impl_layout = QVBoxLayout()
        impl_group.setLayout(impl_layout)
        layout.addWidget(impl_group)
        
        # ラジオボタングループ
        self.impl_button_group = QButtonGroup(self)
        
        # 既存の実装を使用するラジオボタン
        self.use_legacy_radio = QRadioButton("既存の実装を使用")
        self.impl_button_group.addButton(self.use_legacy_radio, 0)
        impl_layout.addWidget(self.use_legacy_radio)
        
        # 新しい実装を使用するラジオボタン
        self.use_new_radio = QRadioButton("新しい実装を使用")
        self.impl_button_group.addButton(self.use_new_radio, 1)
        impl_layout.addWidget(self.use_new_radio)
        
        # ブリッジ実装を使用するラジオボタン
        self.use_bridge_radio = QRadioButton("ブリッジ実装を使用（両方を表示）")
        self.impl_button_group.addButton(self.use_bridge_radio, 2)
        impl_layout.addWidget(self.use_bridge_radio)
        
        # 現在の設定に基づいてラジオボタンを設定
        self.use_new_radio.setChecked(USE_NEW_TABLE_IMPLEMENTATION)
        self.use_legacy_radio.setChecked(not USE_NEW_TABLE_IMPLEMENTATION)
        
        # シグナルの接続
        self.impl_button_group.buttonClicked.connect(self.on_implementation_changed)
        
        # 適用ボタン
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.apply_button = QPushButton("適用")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        # 説明テキスト
        info_text = """
        <p><b>既存の実装</b>：オリジナルのテーブルウィジェットを使用します。</p>
        <p><b>新しい実装</b>：リファクタリングされたテーブルウィジェットを使用します。</p>
        <p><b>ブリッジ実装</b>：両方のウィジェットを表示して比較できます。</p>
        <p>注意：設定を変更するとアプリケーションの再起動が必要です。</p>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # スペースフィラーを追加
        layout.addStretch()
        
    def on_implementation_changed(self, button):
        """実装の選択が変更された時のハンドラ"""
        self.apply_button.setEnabled(True)
        
    def apply_settings(self):
        """設定を適用する"""
        selected_id = self.impl_button_group.checkedId()
        
        if selected_id == 1:  # 新しい実装
            set_use_new_table_implementation(True)
        elif selected_id == 0:  # 既存の実装
            set_use_new_table_implementation(False)
        elif selected_id == 2:  # ブリッジ実装
            # ブリッジ実装の設定は別の方法で処理する必要がある
            # 現在の実装ではサポートされていない
            pass
            
        # 設定変更シグナルを発行
        self.settings_changed.emit()
        
        # ボタンを無効化
        self.apply_button.setEnabled(False)
