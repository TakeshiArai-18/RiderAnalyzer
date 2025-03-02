from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox,
                             QDoubleSpinBox, QCheckBox, QColorDialog, QGridLayout, QWidget,
                             QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from app.config_manager import ConfigManager

class ColorButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._color = QColor("#FFFFFF")
        self.clicked.connect(self._choose_color)
        self._update_style()

    def _choose_color(self):
        color = QColorDialog.getColor(self._color, self)
        if color.isValid():
            self._color = color
            self._update_style()

    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color.name()};
                border: 1px solid #CCCCCC;
                padding: 5px;
            }}
        """)

    def get_color(self):
        return self._color.name()

    def set_color(self, color_str):
        if color_str:
            self._color = QColor(color_str)
            self._update_style()

class ItemManagerWidget(QWidget):
    """ライダーやタイヤなどの項目管理用の共通ウィジェット"""
    
    def __init__(self, parent=None, config_manager=None, item_type=None):
        """
        初期化
        
        Parameters:
        -----------
        parent : QWidget
            親ウィジェット
        config_manager : ConfigManager
            設定管理オブジェクト
        item_type : str
            管理する項目のタイプ（"rider" または "tire"）
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.item_type = item_type
        self.item_rows = {}  # ID:行インデックスのマッピング
        
        # メソッド名を動的に設定
        self.get_items_method = f"get_{item_type}s_list"
        self.add_item_method = f"add_{item_type}"
        self.delete_item_method = f"delete_{item_type}"
        self.update_item_method = f"update_{item_type}"
        
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
        self.add_button.clicked.connect(self.add_item)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        
        self.form_layout.addLayout(buttons_layout, 4, 0, 1, 2)
        form_group.setLayout(self.form_layout)
        layout.addWidget(form_group)
        
        # テーブルの行選択時のイベント
        self.table.itemSelectionChanged.connect(self.on_item_selection_changed)
        
        # フォームカスタマイズのチャンス（サブクラスで上書きする想定）
        self.customize_form()
        
        # アイテムリストを表示
        self.populate_items_list()
    
    def customize_form(self):
        """フォームをカスタマイズするためのメソッド（サブクラスでオーバーライド可能）"""
        pass
    
    def populate_items_list(self):
        """アイテムリストをテーブルに表示"""
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
            self.table.setItem(row, 3, default_item)
        
        # 選択状態をリセット
        self.reset_form()
        self.delete_button.setEnabled(False)
    
    def on_item_selection_changed(self):
        """テーブルで行が選択されたときの処理"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            # 削除ボタンを有効化
            self.delete_button.setEnabled(True)
        else:
            # 選択解除時は削除ボタンを無効化
            self.delete_button.setEnabled(False)
    
    def add_item(self):
        """新しいアイテムを追加"""
        # フォームからデータを取得
        if self.item_type == "rider":
            new_item = {
                "name": self.name_edit.text() or f"New {self.item_type.capitalize()}",
                "bike": self.second_edit.text(),
                "color": self.color_button.get_color(),
                "default": self.default_checkbox.isChecked()
            }
        else:  # tire
            new_item = {
                "name": self.name_edit.text() or f"New {self.item_type.capitalize()}",
                "description": self.second_edit.text(),
                "color": self.color_button.get_color(),
                "default": self.default_checkbox.isChecked()
            }
        
        # データベースに追加
        add_func = getattr(self.config_manager, self.add_item_method)
        add_func(new_item)
        
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
    
    def get_items_dict(self):
        """
        現在のアイテムの状態をすべて取得
        
        Returns:
        --------
        dict: {item_id: item_data, ...}
        """
        items_dict = {}
        
        for i in range(self.table.rowCount()):
            item_id = self.table.item(i, 0).data(Qt.UserRole)
            
            if self.item_type == "rider":
                item_data = {
                    "name": self.table.item(i, 0).text(),
                    "bike": self.table.item(i, 1).text(),
                    "color": self.table.item(i, 2).background().color().name(),
                    "default": self.table.item(i, 3).checkState() == Qt.Checked
                }
            else:  # tire
                item_data = {
                    "name": self.table.item(i, 0).text(),
                    "description": self.table.item(i, 1).text(),
                    "color": self.table.item(i, 2).background().color().name(),
                    "default": self.table.item(i, 3).checkState() == Qt.Checked
                }
            
            items_dict[item_id] = item_data
        
        return items_dict

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

class StatsColorSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._init_ui()

    def _init_ui(self):
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
        self.setLayout(layout)

        # 現在の設定を読み込む
        self._load_current_settings()

    def _load_current_settings(self):
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

    def get_settings(self):
        return {
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

class SettingsDialog(QDialog):
    settings_updated = pyqtSignal(dict)  # 設定更新シグナルを追加

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager if config_manager else parent.config_manager
        self.setWindowTitle("設定")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # タブウィジェットを作成
        tab_widget = QTabWidget()
        
        # 各タブを追加
        tab_widget.addTab(self.create_csv_tab(), "CSVインポート")
        tab_widget.addTab(self.create_graph_tab(), "グラフ")
        tab_widget.addTab(self.create_color_tab(), "カラー")
        tab_widget.addTab(self.create_session_tab(), "セッション")
        tab_widget.addTab(self.create_stats_color_tab(), "統計カラー")
        tab_widget.addTab(self.create_riders_tab(), "ライダー")
        tab_widget.addTab(self.create_tires_tab(), "タイヤ")
        
        layout.addWidget(tab_widget)
        
        # OKボタン
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_settings)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
        
    def create_csv_tab(self):
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
        return widget

    def create_graph_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # グラフ表示グループ
        graph_display_group = QGroupBox("グラフ表示設定")
        graph_display_layout = QGridLayout()
        
        # グラフウィンドウの表示/非表示設定
        self.show_graph_window_checkbox = QCheckBox("データ読み込み時にグラフウィンドウを表示する")
        show_graph = self.config_manager.get_setting("app_settings", "show_graph_window")
        self.show_graph_window_checkbox.setChecked(show_graph)
        graph_display_layout.addWidget(self.show_graph_window_checkbox, 0, 0, 1, 2)
        
        # グリッド表示のチェックボックス
        self.grid_checkbox = QCheckBox("グリッド線を表示")
        grid_enabled = self.config_manager.get_setting("graph_settings", "grid")
        self.grid_checkbox.setChecked(grid_enabled)
        graph_display_layout.addWidget(self.grid_checkbox, 1, 0, 1, 2)
        
        graph_display_group.setLayout(graph_display_layout)
        layout.addWidget(graph_display_group)
        
        # 基本設定の追加
        basic_group = QGroupBox("基本設定")
        basic_layout = QVBoxLayout()
        
        # グラフタイプ
        self.graph_type = QComboBox()
        self.graph_type.addItems(["Line", "Bar", "Scatter"])
        self.graph_type.setCurrentText(self.config_manager.get_setting("graph", "type") or "Line")
        basic_layout.addWidget(QLabel("デフォルトグラフタイプ:"))
        basic_layout.addWidget(self.graph_type)
        
        # 線の太さ
        self.line_width = QDoubleSpinBox()
        self.line_width.setRange(0.5, 5.0)
        self.line_width.setSingleStep(0.5)
        line_width = self.config_manager.get_setting("graph", "line_width")
        self.line_width.setValue(float(line_width) if line_width else 1.5)
        basic_layout.addWidget(QLabel("線の太さ:"))
        basic_layout.addWidget(self.line_width)

        # マーカーサイズ
        self.marker_size = QDoubleSpinBox()
        self.marker_size.setRange(1.0, 10.0)
        self.marker_size.setSingleStep(0.5)
        marker_size = self.config_manager.get_setting("graph", "marker_size")
        self.marker_size.setValue(float(marker_size) if marker_size else 6.0)
        basic_layout.addWidget(QLabel("マーカーサイズ:"))
        basic_layout.addWidget(self.marker_size)

        # マーカースタイル
        self.marker_style = QComboBox()
        self.marker_style.addItems(["o", "s", "^", "v", "D"])
        self.marker_style.setCurrentText(self.config_manager.get_setting("graph", "marker_style") or "o")
        basic_layout.addWidget(QLabel("マーカースタイル:"))
        basic_layout.addWidget(self.marker_style)

        # 線のスタイル
        self.line_style = QComboBox()
        self.line_style.addItems(["-", "--", "-.", ":"])
        self.line_style.setCurrentText(self.config_manager.get_setting("graph", "line_style") or "-")
        basic_layout.addWidget(QLabel("線のスタイル:"))
        basic_layout.addWidget(self.line_style)

        # グリッド表示
        self.show_grid = QCheckBox("グリッド表示")
        self.show_grid.setChecked(self.config_manager.get_setting("graph", "show_grid") == "Yes")
        basic_layout.addWidget(self.show_grid)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # ラップタイムトレンド設定
        trend_group = QGroupBox("ラップタイムトレンド設定")
        trend_layout = QVBoxLayout()
        
        # 移動平均のウィンドウサイズ
        self.lap_trend_window_size = QSpinBox()
        self.lap_trend_window_size.setRange(2, 10)
        self.lap_trend_window_size.setValue(int(self.config_manager.get_setting("graph", "lap_trend_window_size") or 5))
        trend_layout.addWidget(QLabel("移動平均のウィンドウサイズ:"))
        trend_layout.addWidget(self.lap_trend_window_size)
        
        trend_group.setLayout(trend_layout)
        layout.addWidget(trend_group)
        
        # レーダーチャート設定
        radar_group = QGroupBox("レーダーチャート設定")
        radar_layout = QVBoxLayout()
        
        # 移動平均のウィンドウサイズ
        self.radar_window_size = QSpinBox()
        self.radar_window_size.setRange(2, 10)
        self.radar_window_size.setValue(int(self.config_manager.get_setting("graph", "radar_window_size") or 3))
        radar_layout.addWidget(QLabel("移動平均のウィンドウサイズ:"))
        radar_layout.addWidget(self.radar_window_size)
        
        # 標準偏差の透明度
        self.radar_alpha = QDoubleSpinBox()
        self.radar_alpha.setRange(0.0, 1.0)
        self.radar_alpha.setSingleStep(0.1)
        self.radar_alpha.setValue(float(self.config_manager.get_setting("graph", "radar_alpha") or 0.2))
        radar_layout.addWidget(QLabel("標準偏差の透明度:"))
        radar_layout.addWidget(self.radar_alpha)
        
        # ライダー毎の色設定
        self.rider_colors = {}
        riders = self.config_manager.get_setting("graph", "known_riders") or []
        if riders:
            color_group = QGroupBox("ライダー別カラー設定")
            color_layout = QGridLayout()
            for i, rider in enumerate(riders):
                color_button = ColorButton(rider)
                saved_color = self.config_manager.get_setting("graph", f"rider_color_{rider}")
                if saved_color:
                    color_button.set_color(saved_color)
                self.rider_colors[rider] = color_button
                color_layout.addWidget(QLabel(rider), i, 0)
                color_layout.addWidget(color_button, i, 1)
            color_group.setLayout(color_layout)
            radar_layout.addWidget(color_group)
        
        radar_group.setLayout(radar_layout)
        layout.addWidget(radar_group)
        
        widget.setLayout(layout)
        return widget

    def create_color_tab(self):
        widget = QGroupBox("色設定")
        layout = QVBoxLayout()
        
        # 最速ラップの色
        fastest_layout = QHBoxLayout()
        fastest_layout.addWidget(QLabel("最速ラップの色:"))
        self.fastest_lap_button = QPushButton()
        self.fastest_lap_button.setStyleSheet(f"background-color: {self.config_manager.get_setting('color', 'fastest_lap') or '#00ff00'}")
        self.fastest_lap_button.clicked.connect(lambda: self.pick_color(self.fastest_lap_button))
        fastest_layout.addWidget(self.fastest_lap_button)
        layout.addLayout(fastest_layout)
        
        # 最遅ラップの色
        slowest_layout = QHBoxLayout()
        slowest_layout.addWidget(QLabel("最遅ラップの色:"))
        self.slowest_lap_button = QPushButton()
        self.slowest_lap_button.setStyleSheet(f"background-color: {self.config_manager.get_setting('color', 'slowest_lap') or '#ff0000'}")
        self.slowest_lap_button.clicked.connect(lambda: self.pick_color(self.slowest_lap_button))
        slowest_layout.addWidget(self.slowest_lap_button)
        layout.addLayout(slowest_layout)
        
        # 通常ラップの色
        normal_layout = QHBoxLayout()
        normal_layout.addWidget(QLabel("通常ラップの色:"))
        self.normal_lap_button = QPushButton()
        self.normal_lap_button.setStyleSheet(f"background-color: {self.config_manager.get_setting('color', 'normal_lap') or '#ffffff'}")
        self.normal_lap_button.clicked.connect(lambda: self.pick_color(self.normal_lap_button))
        normal_layout.addWidget(self.normal_lap_button)
        layout.addLayout(normal_layout)
        
        widget.setLayout(layout)
        return widget

    def create_session_tab(self):
        widget = QGroupBox("セッション設定")
        layout = QVBoxLayout()
        
        # セッション情報
        session_group = QGroupBox("セッション情報")
        session_layout = QVBoxLayout()
        
        # セッション名
        session_name_layout = QHBoxLayout()
        session_name_layout.addWidget(QLabel("セッション名:"))
        self.session_name = QLineEdit()
        current_session = self.config_manager.get_setting("session", "settings")
        if current_session and isinstance(current_session, dict):
            self.session_name.setText(current_session.get("session", {}).get("name", ""))
        session_name_layout.addWidget(self.session_name)
        session_layout.addLayout(session_name_layout)
        
        # サーキット名
        circuit_layout = QHBoxLayout()
        circuit_layout.addWidget(QLabel("サーキット:"))
        self.circuit_name = QLineEdit()
        if current_session and isinstance(current_session, dict):
            self.circuit_name.setText(current_session.get("session", {}).get("circuit", ""))
        circuit_layout.addWidget(self.circuit_name)
        session_layout.addLayout(circuit_layout)
        
        # 日付
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日付:"))
        self.session_date = QLineEdit()
        self.session_date.setPlaceholderText("YYYY-MM-DD")
        if current_session and isinstance(current_session, dict):
            self.session_date.setText(current_session.get("session", {}).get("date", ""))
        date_layout.addWidget(self.session_date)
        session_layout.addLayout(date_layout)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # ライダー情報
        rider_group = QGroupBox("ライダー情報")
        rider_layout = QVBoxLayout()
        
        # ライダー名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("ライダー名:"))
        self.rider_name = QLineEdit()
        if current_session and isinstance(current_session, dict):
            self.rider_name.setText(current_session.get("rider", {}).get("name", ""))
        name_layout.addWidget(self.rider_name)
        rider_layout.addLayout(name_layout)
        
        # バイク
        bike_layout = QHBoxLayout()
        bike_layout.addWidget(QLabel("バイク:"))
        self.bike_name = QLineEdit()
        if current_session and isinstance(current_session, dict):
            self.bike_name.setText(current_session.get("rider", {}).get("bike", ""))
        bike_layout.addWidget(self.bike_name)
        rider_layout.addLayout(bike_layout)
        
        rider_group.setLayout(rider_layout)
        layout.addWidget(rider_group)
        
        # コンディション情報
        condition_group = QGroupBox("コンディション")
        condition_layout = QVBoxLayout()
        
        # タイヤ選択
        tire_layout = QHBoxLayout()
        tire_layout.addWidget(QLabel("タイヤ:"))
        self.tire_combo = QComboBox()
        self.tire_combo.addItems(["ソフト", "ミディアム", "ハード"])
        if current_session and isinstance(current_session, dict):
            current_tire = current_session.get("conditions", {}).get("tire", "")
            if current_tire:
                self.tire_combo.setCurrentText(current_tire)
        tire_layout.addWidget(self.tire_combo)
        condition_layout.addLayout(tire_layout)
        
        # 天候
        weather_layout = QHBoxLayout()
        weather_layout.addWidget(QLabel("天候:"))
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["晴れ", "雨", "小雨"])
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
        
        widget.setLayout(layout)
        return widget

    def create_stats_color_tab(self):
        self.stats_color_settings = StatsColorSettingsWidget(self.config_manager)
        return self.stats_color_settings

    def create_riders_tab(self):
        """ライダー管理タブを作成"""
        # 新しいRiderManagerWidgetを使用
        self.rider_manager = RiderManagerWidget(self, self.config_manager)
        return self.rider_manager
    
    def create_tires_tab(self):
        """タイヤ管理タブを作成"""
        # 新しいTireManagerWidgetを使用
        self.tire_manager = TireManagerWidget(self, self.config_manager)
        return self.tire_manager
    
    def save_settings(self):
        # CSVカラム設定を保存
        csv_columns = {
            "lap_time": self.lap_time_col.text() or "LapTime",
            "sector1": self.sector1_col.text() or "Sector1",
            "sector2": self.sector2_col.text() or "Sector2",
            "sector3": self.sector3_col.text() or "Sector3"
        }
        self.config_manager.update_setting("csv", "columns", csv_columns)
        
        # グラフ設定を保存
        self.config_manager.set_setting("graph", "type", self.graph_type.currentText())
        self.config_manager.set_setting("graph", "line_width", str(self.line_width.value()))
        self.config_manager.set_setting("graph", "marker_size", str(self.marker_size.value()))
        self.config_manager.set_setting("graph", "marker_style", self.marker_style.currentText())
        self.config_manager.set_setting("graph", "line_style", self.line_style.currentText())
        self.config_manager.set_setting("graph", "show_grid", "Yes" if self.show_grid.isChecked() else "No")
        
        # グラフウィンドウの表示/非表示設定を保存
        self.config_manager.update_setting("app_settings", "show_graph_window", self.show_graph_window_checkbox.isChecked())
        
        # ラップタイムトレンド設定の保存
        self.config_manager.set_setting("graph", "lap_trend_window_size", str(self.lap_trend_window_size.value()))
        
        # レーダーチャート設定の保存
        self.config_manager.set_setting("graph", "radar_window_size", str(self.radar_window_size.value()))
        self.config_manager.set_setting("graph", "radar_alpha", str(self.radar_alpha.value()))
        
        # ライダー色設定の保存
        for rider, color_button in self.rider_colors.items():
            self.config_manager.set_setting("graph", f"rider_color_{rider}", color_button.get_color())
        
        # 色設定を保存
        color_settings = {
            "fastest_lap": getattr(self.fastest_lap_button, 'color', '#00ff00'),
            "slowest_lap": getattr(self.slowest_lap_button, 'color', '#ff0000'),
            "normal_lap": getattr(self.normal_lap_button, 'color', '#ffffff')
        }
        self.config_manager.update_setting("color", "settings", color_settings)
        
        # 統計カラー設定を保存
        stats_color_settings = self.stats_color_settings.get_settings()
        self.config_manager.update_setting("stats_table_settings", "settings", stats_color_settings)
        
        # セッション設定を保存
        session_settings = {
            "session": {
                "name": self.session_name.text() or "Default Session",
                "circuit": self.circuit_name.text() or "Default Circuit",
                "date": self.session_date.text() or ""
            },
            "rider": {
                "name": self.rider_name.text() or "Default Rider",
                "bike": self.bike_name.text() or ""
            },
            "conditions": {
                "tire": self.tire_combo.currentText(),
                "weather": self.weather_combo.currentText(),
                "air_temp": self.air_temp.value(),
                "track_temp": self.track_temp.value()
            }
        }
        self.config_manager.update_setting("session", "settings", session_settings)
        
        # ライダー設定を保存
        try:
            # 新しいRiderManagerWidgetから情報を取得
            riders_data = self.rider_manager.get_items_dict()
            for rider_id, rider_data in riders_data.items():
                self.config_manager.update_rider(rider_id, rider_data)
        except Exception as e:
            print(f"Error saving rider settings: {e}")
        
        # タイヤ設定を保存
        try:
            # 新しいTireManagerWidgetから情報を取得
            tires_data = self.tire_manager.get_items_dict()
            for tire_id, tire_data in tires_data.items():
                self.config_manager.update_tire(tire_id, tire_data)
        except Exception as e:
            print(f"Error saving tire settings: {e}")
        
        self.config_manager.save_config()
        self.settings_updated.emit(session_settings)
        self.accept()

    def pick_color(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}")
            button.color = color.name()