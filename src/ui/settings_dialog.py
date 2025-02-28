from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox,
                             QDoubleSpinBox, QCheckBox, QColorDialog, QGridLayout, QWidget,
                             QSpinBox)
from PyQt5.QtCore import pyqtSignal
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
        widget = QWidget()
        layout = QVBoxLayout()
        
        # ライダーリスト用のグループボックス
        rider_group = QGroupBox("登録済みライダー")
        rider_layout = QVBoxLayout()
        
        # ライダーリストを表示
        self.riders_layout = QVBoxLayout()
        self.populate_riders_list()
        rider_layout.addLayout(self.riders_layout)
        
        # 新規ライダー追加ボタン
        add_rider_button = QPushButton("ライダーを追加")
        add_rider_button.clicked.connect(self.add_rider)
        rider_layout.addWidget(add_rider_button)
        
        rider_group.setLayout(rider_layout)
        layout.addWidget(rider_group)
        
        # ライダー設定保存用
        self.rider_editors = {}
        self.rider_color_buttons = {}
        
        widget.setLayout(layout)
        return widget
    
    def populate_riders_list(self):
        """ライダーリストを表示"""
        # まず既存のウィジェットをクリア
        for i in reversed(range(self.riders_layout.count())):
            widget = self.riders_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # 保存用の辞書をクリア
        self.rider_editors = {}
        self.rider_color_buttons = {}
        
        # ライダーリストを取得
        riders_list = self.config_manager.get_riders_list()
        
        for rider in riders_list:
            # ライダー情報表示用のウィジェット
            rider_widget = QWidget()
            rider_layout = QGridLayout()
            rider_widget.setLayout(rider_layout)
            
            # ライダー名
            rider_layout.addWidget(QLabel("名前:"), 0, 0)
            name_edit = QLineEdit(rider.get("name", ""))
            rider_layout.addWidget(name_edit, 0, 1)
            
            # バイク情報
            rider_layout.addWidget(QLabel("バイク:"), 1, 0)
            bike_edit = QLineEdit(rider.get("bike", ""))
            rider_layout.addWidget(bike_edit, 1, 1)
            
            # 色設定
            rider_layout.addWidget(QLabel("カラー:"), 2, 0)
            color_button = ColorButton("")
            color_button.set_color(rider.get("color", "#1f77b4"))
            rider_layout.addWidget(color_button, 2, 1)
            
            # デフォルト設定
            default_checkbox = QCheckBox("デフォルト")
            default_checkbox.setChecked(rider.get("default", False))
            rider_layout.addWidget(default_checkbox, 3, 0, 1, 2)
            
            # 削除ボタン
            delete_button = QPushButton("削除")
            rider_id = rider.get("id")
            delete_button.clicked.connect(lambda checked, rid=rider_id: self.delete_rider(rid))
            rider_layout.addWidget(delete_button, 4, 0, 1, 2)
            
            # ライダー情報をレイアウトに追加
            self.riders_layout.addWidget(rider_widget)
            
            # 保存用の辞書に追加
            self.rider_editors[rider_id] = {
                "name": name_edit,
                "bike": bike_edit,
                "color": color_button,
                "default": default_checkbox
            }
    
    def add_rider(self):
        """新しいライダーを追加"""
        # 新しいライダーデータを作成
        new_rider = {
            "name": "New Rider",
            "bike": "",
            "color": "#1f77b4",
            "default": False
        }
        
        # データベースに追加
        rider_id = self.config_manager.add_rider(new_rider)
        
        # 表示を更新
        self.populate_riders_list()
    
    def delete_rider(self, rider_id):
        """ライダーを削除"""
        # データベースから削除
        self.config_manager.delete_rider(rider_id)
        
        # 表示を更新
        self.populate_riders_list()
    
    def create_tires_tab(self):
        """タイヤ管理タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # タイヤリスト用のグループボックス
        tire_group = QGroupBox("登録済みタイヤ")
        tire_layout = QVBoxLayout()
        
        # タイヤリストを表示
        self.tires_layout = QVBoxLayout()
        self.populate_tires_list()
        tire_layout.addLayout(self.tires_layout)
        
        # 新規タイヤ追加ボタン
        add_tire_button = QPushButton("タイヤを追加")
        add_tire_button.clicked.connect(self.add_tire)
        tire_layout.addWidget(add_tire_button)
        
        tire_group.setLayout(tire_layout)
        layout.addWidget(tire_group)
        
        # タイヤ設定保存用
        self.tire_editors = {}
        
        widget.setLayout(layout)
        return widget
    
    def populate_tires_list(self):
        """タイヤリストを表示"""
        # まず既存のウィジェットをクリア
        for i in reversed(range(self.tires_layout.count())):
            widget = self.tires_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # 保存用の辞書をクリア
        self.tire_editors = {}
        
        # タイヤリストを取得
        tires_list = self.config_manager.get_tires_list()
        
        for tire in tires_list:
            # タイヤ情報表示用のウィジェット
            tire_widget = QWidget()
            tire_layout = QGridLayout()
            tire_widget.setLayout(tire_layout)
            
            # タイヤ名
            tire_layout.addWidget(QLabel("名前:"), 0, 0)
            name_edit = QLineEdit(tire.get("name", ""))
            tire_layout.addWidget(name_edit, 0, 1)
            
            # 説明
            tire_layout.addWidget(QLabel("説明:"), 1, 0)
            description_edit = QLineEdit(tire.get("description", ""))
            tire_layout.addWidget(description_edit, 1, 1)
            
            # 色設定
            tire_layout.addWidget(QLabel("カラー:"), 2, 0)
            color_button = ColorButton("")
            color_button.set_color(tire.get("color", "#000000"))
            tire_layout.addWidget(color_button, 2, 1)
            
            # デフォルト設定
            default_checkbox = QCheckBox("デフォルト")
            default_checkbox.setChecked(tire.get("default", False))
            tire_layout.addWidget(default_checkbox, 3, 0, 1, 2)
            
            # 削除ボタン
            delete_button = QPushButton("削除")
            tire_id = tire.get("id")
            delete_button.clicked.connect(lambda checked, tid=tire_id: self.delete_tire(tid))
            tire_layout.addWidget(delete_button, 4, 0, 1, 2)
            
            # タイヤ情報をレイアウトに追加
            self.tires_layout.addWidget(tire_widget)
            
            # 保存用の辞書に追加
            self.tire_editors[tire_id] = {
                "name": name_edit,
                "description": description_edit,
                "color": color_button,
                "default": default_checkbox
            }
    
    def add_tire(self):
        """新しいタイヤを追加"""
        # 新しいタイヤデータを作成
        new_tire = {
            "name": "New Tire",
            "description": "",
            "color": "#000000",
            "default": False
        }
        
        # データベースに追加
        tire_id = self.config_manager.add_tire(new_tire)
        
        # 表示を更新
        self.populate_tires_list()
    
    def delete_tire(self, tire_id):
        """タイヤを削除"""
        # データベースから削除
        self.config_manager.delete_tire(tire_id)
        
        # 表示を更新
        self.populate_tires_list()
    
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
        
        # 統計色設定を保存
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
        for rider_id, editor in self.rider_editors.items():
            rider_settings = {
                "name": editor["name"].text(),
                "bike": editor["bike"].text(),
                "color": editor["color"].get_color(),
                "default": editor["default"].isChecked()
            }
            self.config_manager.update_rider(rider_id, rider_settings)
        
        # タイヤ設定を保存
        for tire_id, editor in self.tire_editors.items():
            tire_settings = {
                "name": editor["name"].text(),
                "description": editor["description"].text(),
                "color": editor["color"].get_color(),
                "default": editor["default"].isChecked()
            }
            self.config_manager.update_tire(tire_id, tire_settings)
        
        self.config_manager.save_config()
        self.settings_updated.emit(session_settings)
        self.accept()

    def pick_color(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}")
            button.color = color.name()