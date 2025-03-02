"""
グラフ設定タブ
"""
from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QComboBox, QDoubleSpinBox, 
                            QCheckBox, QSpinBox, QGridLayout, QGroupBox)
from ui.settings.base_settings_widget import BaseSettingsWidget
from ui.widgets.color_button import ColorButton

class GraphSettingsWidget(BaseSettingsWidget):
    """グラフ設定を管理するウィジェット"""
    
    def setup_ui(self):
        """UIのセットアップ"""
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
        
        self.setLayout(layout)
    
    def save_settings(self):
        """グラフ設定を保存"""
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
