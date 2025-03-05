from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                                 QPushButton, QFrame, QFileDialog, QLabel, QSizePolicy)
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import numpy as np
from app.analyzer import LapTimeAnalyzer
import pandas as pd
from utils.time_converter import TimeConverter

class GraphWidget(QWidget):
    def __init__(self, analyzer: LapTimeAnalyzer, parent=None):
        super().__init__(parent)
        self.analyzer = analyzer
        self.time_converter = TimeConverter()
        self.data = None
        
        # 日本語フォント設定
        plt.rcParams['font.family'] = ['Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']  
        # Windows日本語フォントを優先的に使用、フォールバックとしてsans-serifを指定
        
        # ウィジェットのサイズポリシーを設定
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        # 全体レイアウト
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # マージンを最小化
        
        # グラフコントロール部分
        control_layout = QHBoxLayout()
        
        # ライダー選択コンボボックス
        self.rider_label = QLabel("Rider:")
        self.rider_combo = QComboBox()
        self.rider_combo.addItem("All Riders")
        self.rider_combo.currentIndexChanged.connect(self.update_graph)
        
        # グラフタイプ選択コンボボックス
        self.graph_type_label = QLabel("Graph Type:")
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Lap Time Trend", "Sector Time Trend", "Sector Time Comparison", "Lap Time Histogram", "Performance Radar"])
        self.graph_type_combo.currentIndexChanged.connect(self.update_graph)
        
        # コントロール部分のレイアウト配置
        control_layout.addWidget(self.rider_label)
        control_layout.addWidget(self.rider_combo)
        control_layout.addWidget(self.graph_type_label)
        control_layout.addWidget(self.graph_type_combo)
        control_layout.addStretch(1)
        
        # グラフ部分の設定
        self.figure = Figure(dpi=100)  # constrained_layoutは使用しない
        self.canvas = FigureCanvas(self.figure)
        
        # サイズポリシーを設定
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(False)  # 高さと幅の比率を固定しない
        self.canvas.setSizePolicy(size_policy)
        
        # ミニマムサイズを設定
        self.canvas.setMinimumSize(400, 300)
        
        # リサイズイベントに対応
        self.canvas.mpl_connect('resize_event', self._on_resize)
        
        # ツールバーの追加
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # レイアウトに追加
        layout.addLayout(control_layout)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)

    def _on_resize(self, event):
        """キャンバスのリサイズイベント処理"""
        # リサイズ時は設定を行い、そのまま更新する（再帰を防ぐ）
        self._configure_figure_size_and_layout()
        
        # データがある場合のみグラフ更新
        if hasattr(self, 'data') and self.data is not None and not self.data.empty:
            # 更新前にフラグを設定して再帰を防ぐ
            self.canvas.draw_idle()

    def update_data(self, data, analysis_results=None):
        """データを更新"""
        try:
            if isinstance(data, list):
                self.data = pd.DataFrame(data)
            else:
                self.data = data

            # ライダーリストを更新
            if self.data is not None and not self.data.empty:
                riders = sorted(self.data['Rider'].unique())
                current = self.rider_combo.currentText()
                
                self.rider_combo.clear()
                self.rider_combo.addItem("All Riders")
                self.rider_combo.addItems(riders)
                
                # 以前選択されていたライダーがリストにある場合は選択を復元
                index = self.rider_combo.findText(current)
                if index >= 0:
                    self.rider_combo.setCurrentIndex(index)
                elif riders:  # リストが空でない場合は最初のライダーを選択
                    self.rider_combo.setCurrentIndex(0)
            
            self.update_graph()
        except Exception as e:
            print(f"Error updating data: {str(e)}")
            self.data = None

    def update_graph(self):
        """グラフを更新"""
        try:
            if self.data is None or self.data.empty:
                return
                
            # グラフをクリア
            self.figure.clear()
            
            # Allライダーモードかどうか
            is_all_riders = self.rider_combo.currentText() == "All Riders"
            
            # 図のサイズと余白を設定
            self._configure_figure_size_and_layout()
            
            # 軸を追加（右側のスペースを予約）
            ax = self.figure.add_subplot(111)
            
            # グラフ設定を取得
            graph_settings = self.analyzer.config_manager.config.get('graph_settings', {})
            line_color = graph_settings.get('line_color', '#1f77b4')
            marker_size = graph_settings.get('marker_size', 6)
            show_grid = graph_settings.get('grid', True)
            title_font_size = graph_settings.get('title_font_size', 14)
            axis_font_size = graph_settings.get('axis_font_size', 12)
            
            # グラフの種類に応じて描画
            graph_type = self.graph_type_combo.currentText()
            if graph_type == "Lap Time Trend":
                self.plot_lap_time_trend(ax, line_width=1.5, marker_size=marker_size, 
                                       marker_style='o', line_style='-')
                # 時間軸のフォーマッタを設定
                ax.yaxis.set_major_formatter(FuncFormatter(self._format_time_ticks))
            elif graph_type == "Lap Time Histogram":
                self.plot_lap_time_histogram(ax)
                # ヒストグラムのY軸は頻度を表示
                ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x)}"))
            elif graph_type == "Sector Time Comparison":
                self.plot_sector_time_comparison(ax, line_width=1.5, marker_size=marker_size, 
                                               marker_style='o')
                # 時間軸のフォーマッタを設定
                ax.yaxis.set_major_formatter(FuncFormatter(self._format_time_ticks))
            elif graph_type == "Sector Time Trend":
                self.plot_sector_time_trend(ax, line_width=1.5, marker_size=marker_size, 
                                          marker_style='o', line_style='-')
                # 時間軸のフォーマッタを設定
                ax.yaxis.set_major_formatter(FuncFormatter(self._format_time_ticks))
            elif graph_type == "Performance Radar":
                self.plot_performance_radar(ax, line_width=1.5, marker_size=marker_size,
                                         marker_style='o', line_style='-')
            
            # フォントサイズを設定
            ax.title.set_size(title_font_size)
            ax.xaxis.label.set_size(axis_font_size)
            ax.yaxis.label.set_size(axis_font_size)
            
            # グリッドを設定
            ax.grid(show_grid)
            
            # 描画
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating graph: {str(e)}")

    def _configure_figure_size_and_layout(self):
        """図のサイズと余白を設定する専用メソッド"""
        # constrained_layoutを無効化（subplots_adjustと競合するため）
        self.figure.set_layout_engine(None)
        
        # キャンバスのピクセルサイズを取得
        width, height = self.canvas.get_width_height()
        dpi = self.figure.get_dpi()
        
        # キャンバスの全領域を使うようにする（係数は使わない）
        self.figure.set_size_inches(width / dpi, height / dpi)
        
        # Allライダーモードかどうか
        is_all_riders = self.rider_combo.currentText() == "All Riders"
        
        # 余白を設定
        if is_all_riders:
            # 右側に余白を増やして凡例のスペースを確保
            self.figure.subplots_adjust(right=0.80, left=0.1, top=0.92, bottom=0.10)
        else:
            # 単一ライダーの場合も右側に余白を確保
            self.figure.subplots_adjust(right=0.85, left=0.1, top=0.92, bottom=0.10)

    def _calculate_moving_average(self, data, window_size=5):
        """データ系列の移動平均を計算"""
        return pd.Series(data).rolling(window=window_size, min_periods=1).mean()

    def plot_lap_time_trend(self, ax, line_width, marker_size, marker_style, line_style):
        """ラップタイムの推移をプロット"""
        if self.data is None:
            return

        # 設定から移動平均のウィンドウサイズを取得
        window_size = int(self.analyzer.config_manager.get_setting("graph_settings", "lap_trend_window_size") or 5)
            
        selected_rider = self.rider_combo.currentText()
        is_all_riders = selected_rider == "All Riders"
        if is_all_riders:
            # 全ライダーのラップタイム推移
            for rider in self.data['Rider'].unique():
                rider_data = self.data[self.data['Rider'] == rider].copy()
                if not rider_data.empty:
                    rider_data = rider_data.sort_values('Lap')
                    times = [self.time_to_seconds(t) for t in rider_data['LapTime']]
                    
                    # ライダーごとの色を取得
                    rider_color = self.analyzer.config_manager.get_rider_color(rider)
                    
                    # 実測値のプロット
                    if rider_color:
                        line = ax.plot(rider_data['Lap'], times,
                               linewidth=line_width,
                               marker='None',
                               linestyle=line_style,
                               label=f'{rider} Lap Time',
                               color=rider_color)
                    else:
                        line = ax.plot(rider_data['Lap'], times,
                               linewidth=line_width,
                               marker='None',
                               linestyle=line_style,
                               label=f'{rider} Lap Time')
                    
                    # 移動平均値のプロット
                    moving_avg = self._calculate_moving_average(times, window_size)
                    line_color = rider_color if rider_color else line[0].get_color()
                    ax.plot(rider_data['Lap'], moving_avg,
                           linewidth=line_width * 0.8,
                           marker='None',
                           linestyle='--',
                           label=f'{rider} Moving Avg',
                           color=line_color,
                           alpha=0.7)
            # 凡例を外部に配置し、必要に応じて縮小表示
            if len(ax.get_lines()) > 0:  # プロット要素があるか確認
                ax.legend(loc='upper right', fontsize='small', frameon=True)
            title = 'Lap Time Trends - All Riders'
        else:
            # 選択されたライダーのラップタイム推移
            rider_data = self.data[self.data['Rider'] == selected_rider].copy()
            if not rider_data.empty:
                rider_data = rider_data.sort_values('Lap')
                times = [self.time_to_seconds(t) for t in rider_data['LapTime']]
                
                # ライダーごとの色を取得
                rider_color = self.analyzer.config_manager.get_rider_color(selected_rider)
                
                # 実測値のプロット
                if rider_color:
                    line = ax.plot(rider_data['Lap'], times,
                           linewidth=line_width,
                           marker='None',
                           linestyle=line_style,
                           label='Lap Time',
                           color=rider_color)
                else:
                    line = ax.plot(rider_data['Lap'], times,
                           linewidth=line_width,
                           marker='None',
                           linestyle=line_style,
                           label='Lap Time')
                
                # 移動平均値のプロット
                moving_avg = self._calculate_moving_average(times, window_size)
                line_color = rider_color if rider_color else line[0].get_color()
                ax.plot(rider_data['Lap'], moving_avg,
                       linewidth=line_width * 0.8,
                       marker='None',
                       linestyle='--',
                       label='Moving Average',
                       color=line_color,
                       alpha=0.7)

            # 凡例を適切な位置に配置
            if len(ax.get_lines()) > 0:  # プロット要素があるか確認
                if selected_rider == "All Riders":
                    ax.legend(loc='upper right', fontsize='small', frameon=True)
                else:
                    ax.legend(loc='upper right', fontsize='small')
            title = 'Lap Time Trends'
        
        ax.set_title(title)
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Time')
        
        # 凡例設定後に明示的にY軸範囲を再設定（上書き防止）
        ax.yaxis.set_major_formatter(FuncFormatter(self._format_time_ticks))

    def _format_time_ticks(self, x, pos):
        """時間を mm:ss.fff 形式にフォーマット"""
        try:
            return self.time_converter.seconds_to_string(x)
        except Exception as e:
            print(f"Error formatting time: {str(e)}")
            return str(x)

    def time_to_seconds(self, time_str):
        """時間文字列を秒に変換"""
        try:
            if not time_str:
                return 0
            return self.time_converter.string_to_seconds(time_str)
        except Exception as e:
            print(f"Error converting time to seconds: {str(e)}")
            return 0

    def plot_lap_time_histogram(self, ax):
        """ラップタイムのヒストグラムを描画"""
        if self.data is None:
            return
            
        selected_rider = self.rider_combo.currentText()
        is_all_riders = selected_rider == "All Riders"
        if is_all_riders:
            # 全ライダーのヒストグラム
            for rider in self.data['Rider'].unique():
                rider_data = self.data[self.data['Rider'] == rider].copy()
                if not rider_data.empty:
                    lap_times = [self.time_to_seconds(t) for t in rider_data['LapTime']]
                    ax.hist(lap_times, alpha=0.5, label=rider, bins=10, density=False)
            if len(ax.patches) > 0:  # ヒストグラムや棒グラフの要素を確認
                ax.legend(loc='upper right', fontsize='small')
            title = 'Lap Time Distribution - All Riders'
        else:
            # 選択されたライダーのヒストグラム
            rider_data = self.data[self.data['Rider'] == selected_rider].copy()
            if not rider_data.empty:
                lap_times = [self.time_to_seconds(t) for t in rider_data['LapTime']]
                ax.hist(lap_times, alpha=0.5, bins=10, density=False)
            title = f'Lap Time Distribution - {selected_rider}'
        
        # X軸を時間表記に変換
        ax.xaxis.set_major_formatter(FuncFormatter(self._format_time_ticks))
        
        # Y軸は頻度（整数）
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x)}"))
        
        ax.set_title(title)
        ax.set_xlabel('Lap Time')
        ax.set_ylabel('Frequency')
        ax.grid(True)

    def plot_sector_time_comparison(self, ax, line_width, marker_size, marker_style):
        """セクタータイムの比較を描画"""
        if self.data is None:
            return
            
        sector_cols = ['Sector1', 'Sector2', 'Sector3']
        selected_rider = self.rider_combo.currentText()
        
        if selected_rider == "All Riders":
            # 全ライダーのセクタータイム比較
            riders = self.data['Rider'].unique()
            x = np.arange(len(sector_cols))
            width = 0.8 / len(riders)
            
            has_valid_data = False  # 有効なデータがあるかのフラグ
            
            for i, rider in enumerate(riders):
                rider_data = self.data[self.data['Rider'] == rider].copy()
                if not rider_data.empty:
                    # 有効なセクタータイムを確認
                    sector_times = [
                        np.mean([self.time_to_seconds(t) for t in rider_data[col] if self._is_valid_time(t)])
                        for col in sector_cols
                    ]
                    
                    # 有効なセクタータイムが存在するか確認
                    if any(not np.isnan(t) for t in sector_times):
                        ax.bar(x + i * width, sector_times, width, label=rider)
                        has_valid_data = True  # 有効なデータがあるとマーク
            
            # 有効なデータがある場合のみ凡例を表示
            if has_valid_data and len(ax.patches) > 0:  # 棒グラフのパッチを確認
                ax.legend(loc='upper right', fontsize='small')
            title = 'Average Sector Times - All Riders'
        else:
            # 選択されたライダーのセクタータイム比較
            rider_data = self.data[self.data['Rider'] == selected_rider].copy()
            has_valid_bars = False  # 有効な棒グラフがあるかのフラグ
            
            if not rider_data.empty:
                sector_times = [
                    np.mean([self.time_to_seconds(t) for t in rider_data[col] if self._is_valid_time(t)])
                    for col in sector_cols
                ]
                
                # 各セクターに個別のラベルを付ける
                for i, sector in enumerate(sector_cols):
                    if not np.isnan(sector_times[i]):  # 有効な値のみプロット
                        ax.bar(i, sector_times[i], 0.8, label=sector)
                        has_valid_bars = True
                
                # 凡例を表示（有効なデータがある場合のみ）
                if has_valid_bars and len(ax.patches) > 0:  # 棒グラフのパッチを確認
                    ax.legend(loc='upper right', fontsize='small')
            title = f'Average Sector Times - {selected_rider}'
        
        ax.set_title(title)
        ax.set_xticks(np.arange(len(sector_cols)))
        ax.set_xticklabels(sector_cols)
        ax.set_xlabel('Sectors')
        ax.set_ylabel('Time')

    def plot_sector_time_trend(self, ax, line_width, marker_size, marker_style, line_style):
        """セクタータイムの推移を描画"""
        if self.data is None:
            return
            
        # 設定から移動平均のウィンドウサイズを取得
        window_size = int(self.analyzer.config_manager.get_setting("graph_settings", "lap_trend_window_size") or 5)
            
        sector_cols = ['Sector1', 'Sector2', 'Sector3']
        selected_rider = self.rider_combo.currentText()
        is_all_riders = selected_rider == "All Riders"
        
        # Y軸範囲計算のために事前にすべてのデータを収集
        # 全データからY軸の範囲を決定（事前計算）
        all_sector_times = []
        for rider_name in self.data['Rider'].unique():
            rider_data = self.data[self.data['Rider'] == rider_name].copy()
            if not rider_data.empty:
                for sector in sector_cols:
                    times = [self.time_to_seconds(t) for t in rider_data[sector] if self._is_valid_time(t)]
                    valid_times = [t for t in times if t > 0.1]  # 0.1秒未満は無視
                    all_sector_times.extend(valid_times)
                    
        # 適切なY軸範囲を計算
        y_min, y_max = self._calculate_appropriate_y_range(all_sector_times)
        
        # グラフの描画処理
        if is_all_riders:
            # 全ライダーの各セクタータイムの推移
            legend_handles = []
            legend_labels = []
            for rider in self.data['Rider'].unique():
                rider_data = self.data[self.data['Rider'] == rider].copy()
                if not rider_data.empty:
                    rider_data = rider_data.sort_values('Lap')
                    for sector in sector_cols:
                        times = [self.time_to_seconds(t) for t in rider_data[sector] if self._is_valid_time(t)]
                        # 有効なデータのみを追加（異常値を除外）
                        valid_times = [t for t in times if t > 0.1]  # 0.1秒未満は無視
                        
                        if not valid_times:  # 有効なデータがなければスキップ
                            continue
                        
                        # ライダーごとの色を取得
                        rider_color = self.analyzer.config_manager.get_rider_color(rider)
                        
                        # All Ridersモードでは実測値のプロットはスキップし、移動平均のみ表示する
                        # 実測値用の変数を保持するだけ（移動平均の色用）
                        line_color = rider_color
                        
                        # 移動平均値のプロット
                        if len(valid_times) >= 2:  # 少なくとも2つのデータポイントがある場合
                            moving_avg = self._calculate_moving_average(valid_times, window_size)
                            
                            # 色の取得（カスタム色があればそれを使用）
                            if not line_color:
                                # 固有の色を決定（実測値プロットがないので個別に色を割り当て）
                                color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
                                color_idx = (len(legend_handles)) % len(color_cycle)
                                line_color = color_cycle[color_idx]
                                
                            avg_line = ax.plot(rider_data['Lap'][:len(moving_avg)], moving_avg,
                                    linewidth=line_width * 1.5,  # 線をさらに太くして視認性向上
                                    marker='None',  # マーカーを使用しない
                                    linestyle=line_style,
                                    label=f'{rider} - {sector}',  # 移動平均の表記は省略（凡例を単純化）
                                    color=line_color)
                            
                            # 移動平均線の凡例を保存
                            legend_handles.append(avg_line[0])
                            legend_labels.append(f'{rider} - {sector}')
            
            # 凡例配置の設定（余白調整はupdate_graphで既に設定済み）
            if len(ax.get_lines()) > 0:  # プロット要素があるか確認
                ax.legend(legend_handles, legend_labels, 
                     loc='upper right',
                     fontsize='xx-small',  # フォントサイズをさらに小さく
                     frameon=True,
                     ncol=2,  # 凡例を2列に
                     framealpha=0.9,  # 背景の透明度
                     title='Sectors')  # 凡例にタイトルを追加
            
            # 凡例設定後に明示的にY軸範囲を再設定（上書き防止）
            if y_min is not None and y_max is not None:
                ax.set_ylim(bottom=y_min, top=y_max)
            
            title = 'Sector Time Trends - All Riders'
        else:
            # 選択されたライダーの各セクタータイムの推移
            rider_data = self.data[self.data['Rider'] == selected_rider].copy()
            if not rider_data.empty:
                rider_data = rider_data.sort_values('Lap')
                all_times = []
                for sector in sector_cols:
                    times = [self.time_to_seconds(t) for t in rider_data[sector] if self._is_valid_time(t)]
                    all_times.extend(times)  # 全ての時間を記録
                    
                    # ライダーごとの色を取得
                    rider_color = self.analyzer.config_manager.get_rider_color(selected_rider)
                    
                    # 実測値のプロット
                    if rider_color:
                        line = ax.plot(rider_data['Lap'], times,
                               linewidth=line_width,
                               marker='None',
                               linestyle=line_style,
                               label=sector,
                               color=rider_color)
                    else:
                        line = ax.plot(rider_data['Lap'], times,
                               linewidth=line_width,
                               marker='None',
                               linestyle=line_style,
                               label=sector)
                    
                    # 移動平均値のプロット
                    moving_avg = self._calculate_moving_average(times, window_size)
                    line_color = rider_color if rider_color else line[0].get_color()
                    ax.plot(rider_data['Lap'], moving_avg,
                           linewidth=line_width * 0.8,
                           marker='None',
                           linestyle='--',
                           label=f'{sector} Moving Avg',
                           color=line_color,
                           alpha=0.7)
            
            # 凡例を適切な位置に配置
            if len(ax.get_lines()) > 0:  # プロット要素があるか確認
                ax.legend(loc='upper right', fontsize='small')
            title = f'Sector Time Trends - {selected_rider}'
        
        # Y軸の範囲を適切に設定
        if y_min is not None and y_max is not None:
            ax.set_ylim(bottom=y_min, top=y_max)
        
        ax.set_title(title)
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Time (s)')
        
        # 凡例設定後に明示的にY軸範囲を再設定（上書き防止）
        ax.yaxis.set_major_formatter(FuncFormatter(self._format_time_ticks))

    def _calculate_appropriate_y_range(self, times_list):
        """適切なY軸範囲を計算するヘルパーメソッド"""
        if not times_list:
            return None, None  # データがない場合はNoneを返し、自動スケーリングに任せる
            
        try:
            # データをソート
            sorted_times = sorted(times_list)
            num_samples = len(sorted_times)
            
            if num_samples <= 1:
                # データが1つの場合、その値を中心に範囲を設定
                if num_samples == 1:
                    center = sorted_times[0]
                    return max(0, center - center * 0.2), center + center * 0.2
                else:
                    return None, None  # データがない場合
            
            # 四分位数を計算
            q1_idx = max(0, int(num_samples * 0.25))
            q3_idx = min(num_samples - 1, int(num_samples * 0.75))
            
            q1 = sorted_times[q1_idx]
            q3 = sorted_times[q3_idx]
            
            # 四分位範囲（IQR）を計算
            iqr = q3 - q1
            
            if iqr == 0:  # すべての値が同じ場合
                center = sorted_times[0]
                # 値の20%の範囲を設定
                margin = max(center * 0.2, 0.5)
                return max(0, center - margin), center + margin
            
            # 外れ値を除外した範囲 (1.5 * IQRはボックスプロットの標準的なwhisker)
            lower_bound = max(0, q1 - 1.5 * iqr)
            upper_bound = q3 + 1.5 * iqr
            
            # 実データの最小値と最大値（外れ値を除く）
            valid_data = [t for t in sorted_times if lower_bound <= t <= upper_bound]
            if not valid_data:  # 有効なデータがない場合（極端な外れ値のみの場合）
                valid_data = sorted_times  # すべてのデータを使用
            
            data_min = min(valid_data)
            data_max = max(valid_data)
            
            # データ範囲を計算
            data_range = data_max - data_min
            
            # 範囲にマージンを追加 (データレンジの15%)
            margin = max(data_range * 0.15, 0.5)  # 少なくとも0.5秒、またはデータ範囲の15%
            
            y_min = max(0, data_min - margin)  # 0以上に制限
            y_max = data_max + margin
            
            # 範囲が狭すぎる場合
            if y_max - y_min < 1.0:  # 1秒未満は狭すぎる
                center = (y_min + y_max) / 2
                # 値の大きさに応じたマージンを設定
                relative_margin = max(center * 0.1, 0.5)  # 少なくとも0.5秒、または中心値の10%
                y_min = max(0, center - relative_margin)
                y_max = center + relative_margin
                
            return y_min, y_max
            
        except Exception as e:
            print(f"Y軸の範囲計算でエラーが発生しました: {str(e)}")
            return None, None  # エラーの場合は自動スケーリング

    def _calculate_sector_statistics(self, rider_data, sector_cols, window_size=3):
        """セクター毎の統計情報を計算"""
        stats = {}
        for sector in sector_cols:
            times = pd.Series([self.time_to_seconds(t) for t in rider_data[sector]])
            stats[sector] = {
                'moving_avg': times.rolling(window=window_size, min_periods=1).mean(),
                'std': times.std()
            }
        return stats

    def plot_performance_radar(self, ax, line_width, marker_size, marker_style, line_style):
        """パフォーマンスレーダーチャートを描画"""
        if self.data is None:
            return
            
        # 設定から値を取得
        alpha = float(self.analyzer.config_manager.get_setting("graph_settings", "radar_alpha") or 0.2)
        window_size = int(self.analyzer.config_manager.get_setting("graph_settings", "radar_window_size") or 3)
            
        sector_cols = ['Sector1', 'Sector2', 'Sector3']
        angles = np.linspace(0, 2*np.pi, len(sector_cols), endpoint=False)
        
        selected_rider = self.rider_combo.currentText()
        is_all_riders = selected_rider == "All Riders"
        if is_all_riders:
           # 全ライダーのレーダーチャート
            for rider in self.data['Rider'].unique():
                rider_data = self.data[self.data['Rider'] == rider].copy()
                if not rider_data.empty:
                    # 統計情報の計算
                    stats = self._calculate_sector_statistics(rider_data, sector_cols, window_size)
                    
                    # ライダーごとの色を取得
                    rider_color = self.analyzer.config_manager.get_rider_color(rider)
                    
                    # 移動平均値のプロット
                    sector_times = [stats[col]['moving_avg'].iloc[-1] for col in sector_cols]
                    values = np.concatenate((sector_times, [sector_times[0]]))
                    angles_plot = np.concatenate((angles, [angles[0]]))
                    
                    # メインラインの描画（カスタム色を使用）
                    if rider_color:
                        line = ax.plot(angles_plot, values,
                               linewidth=line_width,
                               marker=marker_style,
                               markersize=marker_size,
                               linestyle=line_style,
                               label=rider,
                               color=rider_color)
                    else:
                        line = ax.plot(angles_plot, values,
                               linewidth=line_width,
                               marker=marker_style,
                               markersize=marker_size,
                               linestyle=line_style,
                               label=rider)
                    
                    # 標準偏差範囲の描画
                    std_values = [stats[col]['std'] for col in sector_cols]
                    std_values = np.concatenate((std_values, [std_values[0]]))
                    upper = values + std_values
                    lower = values - std_values
                    ax.fill_between(angles_plot, lower, upper, 
                                  alpha=alpha, 
                                  color=rider_color if rider_color else line[0].get_color())
                    
            if len(ax.get_lines()) > 0:  # プロット要素があるか確認
                ax.legend(loc='upper right', fontsize='small')
            title = 'Sector Performance - All Riders'
        else:
            # 選択されたライダーのレーダーチャート
            rider_data = self.data[self.data['Rider'] == selected_rider].copy()
            if not rider_data.empty:
                # 統計情報の計算
                stats = self._calculate_sector_statistics(rider_data, sector_cols, window_size)
                
                # ライダーごとの色を取得
                rider_color = self.analyzer.config_manager.get_rider_color(selected_rider)
                
                # 移動平均値のプロット
                sector_times = [stats[col]['moving_avg'].iloc[-1] for col in sector_cols]
                values = np.concatenate((sector_times, [sector_times[0]]))
                angles_plot = np.concatenate((angles, [angles[0]]))
                
                # メインラインの描画（カスタム色を使用）
                if rider_color:
                    line = ax.plot(angles_plot, values,
                           linewidth=line_width,
                           marker=marker_style,
                           markersize=marker_size,
                           linestyle=line_style,
                           color=rider_color)
                else:
                    line = ax.plot(angles_plot, values,
                           linewidth=line_width,
                           marker=marker_style,
                           markersize=marker_size,
                           linestyle=line_style)
                
                # 標準偏差範囲の描画
                std_values = [stats[col]['std'] for col in sector_cols]
                std_values = np.concatenate((std_values, [std_values[0]]))
                upper = values + std_values
                lower = values - std_values
                ax.fill_between(angles_plot, lower, upper, 
                              alpha=alpha, 
                              color=rider_color if rider_color else line[0].get_color())
            title = f'Sector Performance - {selected_rider}'
        
        ax.set_title(title)
        ax.set_xticks(angles)
        ax.set_xticklabels(sector_cols)

    def _is_valid_time(self, time_str):
        """時間文字列が有効かどうかをチェック"""
        if not time_str:
            return False
        try:
            time_val = self.time_to_seconds(time_str)
            return time_val > 0
        except:
            return False