from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QFileDialog, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt
from ui.data_input_widget import DataInputWidget
from ui.graph_widget import GraphWidget
from ui.graph_window import GraphWindow
from ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from ui.base_widgets.statistics_table_widget import StatisticsTableWidget
from ui.settings_dialog import SettingsDialog
from app.analyzer import LapTimeAnalyzer
from app.data_loader import DataLoader
from app.config_manager import ConfigManager
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 設定マネージャーの初期化
        self.config_manager = ConfigManager()
        
        # 以前の形式からの移行確認
        self.config_manager.migrate_to_new_format()
        
        # データローダーとアナライザーの初期化
        self.data_loader = DataLoader(self.config_manager)
        self.analyzer = LapTimeAnalyzer(self.data_loader, self.config_manager)
        
        self.lap_data = None
        self.graph_window = GraphWindow(self.analyzer, self)
        self.initUI()
        
        # ライダーとタイヤ情報の更新
        self.update_riders_and_tires()
        
    def initUI(self):
        """UIの初期化"""
        self.setWindowTitle('RiderCal')
        self.setGeometry(100, 100, 1200, 800)
        
        # メインウィジェットとレイアウト
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # データ入力ウィジェット
        self.data_input = DataInputWidget(config_manager=self.config_manager)
        self.data_input.data_changed.connect(self.on_data_changed)
        
        # ボタンのイベントを接続
        self.data_input.load_json_button.clicked.connect(self.open_json_file)
        self.data_input.load_csv_button.clicked.connect(self.open_csv_file)
        
        layout.addWidget(self.data_input)
        
        # スプリッター（3つのウィジェットを垂直に分割）
        splitter = QSplitter(Qt.Vertical)
        
        # 統計情報テーブル
        self.stats_table = StatisticsTableWidget(self.config_manager, parent=self)
        splitter.addWidget(self.stats_table)
        
        # テーブルウィジェット
        self.table_widget = LapDataTableWidget(parent=self)
        splitter.addWidget(self.table_widget)
        
        # スプリッターの初期サイズ比を設定（グラフ:統計:テーブル = 4:2:4）
        splitter.setSizes([200, 400])
        layout.addWidget(splitter)
        
        main_widget.setLayout(layout)
        
        # メニューバーの設定
        self.setup_menu()
        
        # グラフウィンドウの初期状態を設定
        # データがロードされるまでは表示しない
        self.graph_window.hide()
        
    def setup_menu(self):
        """メニューバーの設定"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu('File')
        
        # JSONを開く
        open_json_action = file_menu.addAction('Open JSON')
        open_json_action.triggered.connect(self.open_json_file)
        
        # CSVを開く
        open_csv_action = file_menu.addAction('Open CSV')
        open_csv_action.triggered.connect(self.open_csv_file)
        
        # 終了
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # 設定メニュー
        settings_menu = menubar.addMenu('Settings')
        session_settings_action = settings_menu.addAction('Session Settings')
        session_settings_action.triggered.connect(self.open_settings_dialog)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        usage_action = help_menu.addAction('Usage Guide')
        usage_action.triggered.connect(self.show_usage_guide)
        
    def open_json_file(self):
        """JSONファイルを開く"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON file', '', 'JSON files (*.json)')
            if file_path:
                try:
                    data = self.data_loader.load_json(file_path)
                    if data and 'lap_data' in data:
                        self.on_data_loaded(data)
                    else:
                        QMessageBox.warning(self, "Warning", "Invalid data format in JSON file")
                except Exception as e:
                    print(f"Error loading JSON file: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to load JSON file: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")

    def open_csv_file(self):
        """CSVファイルを開く"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open CSV file', '', 'CSV files (*.csv)')
            if file_path:
                try:
                    data = self.data_loader.load_csv(file_path)
                    if data and 'lap_data' in data:
                        self.on_data_loaded(data)
                    else:
                        QMessageBox.warning(self, "Warning", "Invalid data format in CSV file")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")

    def open_settings_dialog(self):
        """セッション設定ダイアログを開く"""
        dialog = SettingsDialog(self)
        dialog.settings_updated.connect(self.on_settings_updated)
        dialog.exec_()
        
    def on_data_loaded(self, data):
        """データ読み込み時の処理"""
        try:
            if not data or 'lap_data' not in data:
                return

            # 既存の分析
            analysis_results = self.analyzer.analyze_laps(data['lap_data'])
            
            # 移動平均統計の計算
            moving_stats = self.analyzer.calculate_moving_statistics(data['lap_data'])

            # 各ウィジェットの更新
            self.data_input.update_data(data['lap_data'], analysis_results)
            self.table_widget.update_data(data['lap_data'], analysis_results)
            self.graph_window.update_data(data['lap_data'], analysis_results)
            self.stats_table.update_statistics(moving_stats)
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to process data: {str(e)}")

    def on_data_changed(self, data):
        """データが変更されたときの処理"""
        try:
            if not data:
                return

            # 分析結果を取得
            analysis_results = self.analyzer.analyze_laps(data)

            # 各ウィジェットを更新
            self.table_widget.update_data(data, analysis_results)
            self.graph_window.update_data(data, analysis_results)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update data: {str(e)}")

    def on_settings_updated(self, settings):
        """設定が更新されたときの処理"""
        # 設定変更を保存
        self.config_manager.save_config()
        
        # ライダーとタイヤ情報の更新
        self.update_riders_and_tires()
        
        # グラフウィンドウが存在する場合は更新
        if self.graph_window:
            self.graph_window.graph_widget.update_graph()
            
    def update_riders_and_tires(self):
        """ライダーとタイヤの情報を更新する"""
        # DataInputWidgetのコンボボックスを更新
        self.data_input.update_riders_combo()
        self.data_input.update_tires_combo()

    def show_about(self):
        """アバウトダイアログを表示"""
        QMessageBox.about(self, 'About',
            'Lap Time Analyzer for Rider Performance Visualization\n\n'
            'Version 1.0\n'
            'A powerful tool for analyzing and visualizing lap time data '
            'to help riders improve their performance.\n\n'
            ' 2025 Your Organization')

    def show_usage_guide(self):
        """使用方法ガイドを表示"""
        QMessageBox.information(self, 'Usage Guide',
            '<h3>Quick Start Guide</h3>'
            '<p><b>1. Loading Data:</b></p>'
            '<ul>'
            '<li>Click "File > Open JSON" to load a JSON format lap time data file</li>'
            '<li>Click "File > Open CSV" to load a CSV format lap time data file</li>'
            '</ul>'
            '<p><b>2. Viewing Data:</b></p>'
            '<ul>'
            '<li>The data input section shows session information and allows data entry</li>'
            '<li>The graph section shows various visualizations of lap times</li>'
            '<li>The table shows detailed lap data for each rider</li>'
            '<li>Green rows indicate the fastest laps</li>'
            '<li>Red rows indicate the slowest laps</li>'
            '</ul>'
            '<p><b>3. Analyzing Data:</b></p>'
            '<ul>'
            '<li>Use the graph type selector to switch between different visualizations:</li>'
            '<li>- Lap Time Trend: Shows lap time progression</li>'
            '<li>- Lap Time Histogram: Shows lap time distribution</li>'
            '<li>- Sector Time Comparison: Compare sector performances</li>'
            '<li>- Sector Time Trend: Shows sector time progression</li>'
            '<li>- Performance Radar: Overall performance visualization</li>'
            '</ul>'
            '<p><b>4. Settings:</b></p>'
            '<ul>'
            '<li>Use Settings > Session Settings to configure session information</li>'
            '</ul>')