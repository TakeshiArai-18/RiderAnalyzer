"""
アイテム管理ウィジェット
ライダーやタイヤなどの管理に使用される共通ウィジェット
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QTableWidget, QLabel, QLineEdit, QCheckBox, 
                            QPushButton, QGridLayout, QTableWidgetItem, 
                            QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from ui.widgets.color_button import ColorButton

class ItemManagerWidget(QWidget):
    """ライダーやタイヤなどの項目管理用の共通ウィジェット"""
    
    def __init__(self, parent=None, config_manager=None, item_type="rider"):
        super().__init__(parent)
        self.config_manager = config_manager
        self.item_type = item_type
        self.item_rows = {}
        self.current_edit_id = None  # 編集中のアイテムID
        self.is_updating_table = False  # テーブル更新中フラグ
        
        # メソッド名を生成（item_typeに基づいたメソッド名）
        self.get_items_method = f"get_{item_type}s_list"
        self.add_item_method = f"add_{item_type}"
        self.update_item_method = f"update_{item_type}"  # 更新用メソッド名
        self.delete_item_method = f"delete_{item_type}"
        
        self._init_ui()
    
    def _init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        # テーブル用のグループボックス
        type_name = "ライダー" if self.item_type == "rider" else "タイヤ"
        table_group = QGroupBox(f"登録済み{type_name}")
        table_layout = QVBoxLayout()
        
        # テーブルの作成
        self.table = QTableWidget()
        
        # item_typeに応じてテーブル列を設定
        if self.item_type == "rider":
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["名前", "バイク", "カラー", "デフォルト"])
        else:  # tire
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["名前", "説明", "カラー", "デフォルト"])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 直接編集を無効化
        
        # テーブルのサイズ調整
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table_layout.addWidget(self.table)
        
        # テーブル下部のボタン
        buttons_layout = QHBoxLayout()
        
        # 編集ボタンを追加
        self.edit_button = QPushButton("編集")
        self.edit_button.setEnabled(False)  # 初期状態では無効
        self.edit_button.clicked.connect(self.edit_selected_item)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.setEnabled(False)  # 初期状態では無効
        self.delete_button.clicked.connect(self.delete_selected_item)
        
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        
        table_layout.addLayout(buttons_layout)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # 新規追加・編集用フォーム
        form_group = QGroupBox(f"{type_name}情報")
        self.form_layout = QGridLayout()
        
        # 名前（共通）
        self.form_layout.addWidget(QLabel("名前:"), 0, 0)
        self.name_edit = QLineEdit()
        self.form_layout.addWidget(self.name_edit, 0, 1)
        
        # item_typeに応じて2行目の項目を変更
        if self.item_type == "rider":
            self.form_layout.addWidget(QLabel("バイク:"), 1, 0)
            self.second_edit = QLineEdit()
        else:  # tire
            self.form_layout.addWidget(QLabel("説明:"), 1, 0)
            self.second_edit = QLineEdit()
        
        self.form_layout.addWidget(self.second_edit, 1, 1)
        
        # 色設定（共通）
        self.form_layout.addWidget(QLabel("カラー:"), 2, 0)
        self.color_button = ColorButton("")
        default_color = "#1f77b4" if self.item_type == "rider" else "#000000"
        self.color_button.set_color(default_color)
        self.form_layout.addWidget(self.color_button, 2, 1)
        
        # デフォルト設定（共通）
        self.default_checkbox = QCheckBox("デフォルト")
        self.form_layout.addWidget(self.default_checkbox, 3, 0, 1, 2)
        
        # 追加・更新ボタン
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("追加")
        self.add_button.clicked.connect(self.add_or_update_item)
        
        # キャンセルボタンを追加
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reset_form)
        self.cancel_button.setVisible(False)  # 初期状態では非表示
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.add_button)
        
        self.form_layout.addLayout(buttons_layout, 4, 0, 1, 2)
        form_group.setLayout(self.form_layout)
        layout.addWidget(form_group)
        
        # テーブルの行選択時のイベント
        self.table.itemSelectionChanged.connect(self.on_item_selection_changed)
        
        # テーブルのアイテム変更時のイベント
        self.table.itemChanged.connect(self.on_item_changed)
        
        # フォームカスタマイズのチャンス（サブクラスで上書きする想定）
        self.customize_form()
        
        # アイテムリストを表示
        self.populate_items_list()
    
    def customize_form(self):
        """フォームをカスタマイズするためのメソッド（サブクラスでオーバーライド可能）"""
        pass
    
    def populate_items_list(self):
        """アイテムリストをテーブルに表示"""
        # 更新中フラグをON
        self.is_updating_table = True
        
        try:
            # テーブルをクリア
            self.table.setRowCount(0)
            
            # IDと対応する行インデックスをクリア
            self.item_rows = {}
            
            # リストを取得
            get_list_func = getattr(self.config_manager, self.get_items_method)
            items_list = get_list_func()
            
            # テーブルに追加
            for item in items_list:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item_id = item.get("id")
                self.item_rows[item_id] = row
                
                # 名前
                name_item = QTableWidgetItem(item.get("name", ""))
                name_item.setData(Qt.UserRole, item_id)  # IDを非表示データとして保存
                self.table.setItem(row, 0, name_item)
                
                # 2列目（バイクまたは説明）
                if self.item_type == "rider":
                    second_item = QTableWidgetItem(item.get("bike", ""))
                else:  # tire
                    second_item = QTableWidgetItem(item.get("description", ""))
                self.table.setItem(row, 1, second_item)
                
                # カラー（セルを色で塗る）
                color_item = QTableWidgetItem()
                default_color = "#1f77b4" if self.item_type == "rider" else "#000000"
                color = item.get("color", default_color)
                color_item.setBackground(QColor(color))
                self.table.setItem(row, 2, color_item)
                
                # デフォルト
                default_item = QTableWidgetItem()
                default_item.setCheckState(Qt.Checked if item.get("default", False) else Qt.Unchecked)
                default_item.setFlags(default_item.flags() | Qt.ItemIsUserCheckable)  # チェックボックスを有効化
                self.table.setItem(row, 3, default_item)
            
            # 選択状態をリセット
            self.reset_form()
            self.delete_button.setEnabled(False)
            self.edit_button.setEnabled(False)
        finally:
            # 更新中フラグをOFF
            self.is_updating_table = False
    
    def on_item_selection_changed(self):
        """テーブルで行が選択されたときの処理"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            # 削除ボタンと編集ボタンを有効化
            self.delete_button.setEnabled(True)
            self.edit_button.setEnabled(True)
        else:
            # 選択解除時はボタンを無効化
            self.delete_button.setEnabled(False)
            self.edit_button.setEnabled(False)
    
    def edit_selected_item(self):
        """選択されたアイテムを編集用にフォームにロード"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            item_id = self.table.item(row, 0).data(Qt.UserRole)
            
            # リストからアイテムデータを取得
            get_list_func = getattr(self.config_manager, self.get_items_method)
            items_list = get_list_func()
            
            for item in items_list:
                if item.get("id") == item_id:
                    # フォームにデータをセット
                    self.name_edit.setText(item.get("name", ""))
                    
                    if self.item_type == "rider":
                        self.second_edit.setText(item.get("bike", ""))
                    else:  # tire
                        self.second_edit.setText(item.get("description", ""))
                    
                    self.color_button.set_color(item.get("color", "#1f77b4" if self.item_type == "rider" else "#000000"))
                    self.default_checkbox.setChecked(item.get("default", False))
                    
                    # 編集モードに切り替え
                    self.current_edit_id = item_id
                    self.add_button.setText("更新")
                    self.cancel_button.setVisible(True)
                    break
    
    def add_or_update_item(self):
        """新規追加または更新処理"""
        # フォームからデータを取得
        if self.item_type == "rider":
            item_data = {
                "name": self.name_edit.text() or f"New {self.item_type.capitalize()}",
                "bike": self.second_edit.text(),
                "color": self.color_button.get_color(),
                "default": self.default_checkbox.isChecked()
            }
        else:  # tire
            item_data = {
                "name": self.name_edit.text() or f"New {self.item_type.capitalize()}",
                "description": self.second_edit.text(),
                "color": self.color_button.get_color(),
                "default": self.default_checkbox.isChecked()
            }
        
        # デフォルトチェックボックスがONの場合、他のアイテムのデフォルト設定をOFFにする
        if self.item_type == "rider" and item_data["default"]:
            # 現在のライダーリストを取得
            get_list_func = getattr(self.config_manager, self.get_items_method)
            items_list = get_list_func()
            
            # 現在編集中のアイテムID以外のアイテムで、デフォルト設定がONのものをOFFにする
            for item in items_list:
                item_id = item.get("id")
                # 現在編集中のアイテム以外で、かつデフォルト設定がONの場合
                if (self.current_edit_id is None or item_id != self.current_edit_id) and item.get("default", False):
                    # デフォルト設定をOFFにする
                    item_data_copy = item.copy()
                    item_data_copy["default"] = False
                    
                    # 設定を更新
                    update_func = getattr(self.config_manager, self.update_item_method)
                    update_func(item_id, item_data_copy)
        
        if self.current_edit_id:
            # 更新処理
            update_func = getattr(self.config_manager, self.update_item_method)
            update_func(self.current_edit_id, item_data)
        else:
            # 新規追加処理
            add_func = getattr(self.config_manager, self.add_item_method)
            add_func(item_data)
        
        # 表示を更新
        self.populate_items_list()
        self.reset_form()
    
    def delete_selected_item(self):
        """選択されたアイテムを削除"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            item_id = self.table.item(row, 0).data(Qt.UserRole)
            
            # データベースから削除
            delete_func = getattr(self.config_manager, self.delete_item_method)
            delete_func(item_id)
            
            # 表示を更新
            self.populate_items_list()
    
    def reset_form(self):
        """情報フォームをリセット"""
        self.name_edit.clear()
        self.second_edit.clear()
        default_color = "#1f77b4" if self.item_type == "rider" else "#000000"
        self.color_button.set_color(default_color)
        self.default_checkbox.setChecked(False)
        self.add_button.setText("追加")
        self.current_edit_id = None
        self.cancel_button.setVisible(False)
    
    def get_items_dict(self):
        """全てのアイテムを辞書として取得"""
        items_dict = {}
        
        # リストを取得
        get_list_func = getattr(self.config_manager, self.get_items_method)
        items_list = get_list_func()
        
        # 辞書に変換
        for item in items_list:
            item_id = item.get("id")
            
            if self.item_type == "rider":
                item_data = {
                    "name": item.get("name", ""),
                    "bike": item.get("bike", ""),
                    "color": item.get("color", "#1f77b4"),
                    "default": item.get("default", False)
                }
            else:  # tire
                item_data = {
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "color": item.get("color", "#000000"),
                    "default": item.get("default", False)
                }
            
            items_dict[item_id] = item_data
        
        return items_dict

    def on_item_changed(self, item):
        """テーブルのアイテムが変更されたときの処理"""
        # 更新中フラグがONの場合は何もしない（再帰防止）
        if self.is_updating_table:
            return
            
        # デフォルト列（3列目）のチェックボックスの変更を検知
        if item.column() == 3 and self.item_type == "rider":
            # チェック状態になった場合のみ処理
            if item.checkState() == Qt.Checked:
                # 変更されたアイテムのID取得
                row = item.row()
                changed_item_id = self.table.item(row, 0).data(Qt.UserRole)
                
                # 他のアイテムのデフォルト設定をOFFにする
                self.is_updating_table = True  # 更新中フラグをON
                try:
                    # 現在のデータを取得
                    get_list_func = getattr(self.config_manager, self.get_items_method)
                    items_list = get_list_func()
                    
                    # 変更されたアイテム以外のデフォルト設定をOFFにする
                    for item_data in items_list:
                        item_id = item_data.get("id")
                        if item_id != changed_item_id and item_data.get("default", False):
                            # デフォルト設定をOFFにする
                            item_data_copy = item_data.copy()
                            item_data_copy["default"] = False
                            
                            # 設定を更新
                            update_func = getattr(self.config_manager, self.update_item_method)
                            update_func(item_id, item_data_copy)
                            
                            # テーブル上の表示も更新
                            item_row = self.item_rows.get(item_id)
                            if item_row is not None:
                                default_item = self.table.item(item_row, 3)
                                if default_item:
                                    default_item.setCheckState(Qt.Unchecked)
                    
                    # 変更されたアイテムのデフォルト設定をONにする
                    for item_data in items_list:
                        if item_data.get("id") == changed_item_id:
                            # デフォルト設定をONにする
                            item_data_copy = item_data.copy()
                            item_data_copy["default"] = True
                            
                            # 設定を更新
                            update_func = getattr(self.config_manager, self.update_item_method)
                            update_func(changed_item_id, item_data_copy)
                            break
                            
                finally:
                    self.is_updating_table = False  # 更新中フラグをOFF

class RiderManagerWidget(ItemManagerWidget):
    """ライダー管理用ウィジェット"""
    
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent, config_manager, "rider")
    
    def customize_form(self):
        """ライダー特有のフォームカスタマイズ"""
        # 必要に応じてライダー特有の追加フィールドなどをここに実装
        pass

class TireManagerWidget(ItemManagerWidget):
    """タイヤ管理用ウィジェット"""
    
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent, config_manager, "tire")
    
    def customize_form(self):
        """タイヤ特有のフォームカスタマイズ"""
        # 必要に応じてタイヤ特有の追加フィールドなどをここに実装
        pass
