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
        
        # 解析モードフラグを追加
        self.analysis_mode = False
        
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
        self.setWindowTitle('RiderAnalyzer')
        self.setGeometry(100, 100, 1200, 800)
        
        # メインウィジェットとレイアウト
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # データ入力ウィジェット
        self.data_input = DataInputWidget(config_manager=self.config_manager)
        self.data_input.data_changed.connect(self.on_data_changed)
        self.data_input.analyze_requested.connect(self.on_analyze_requested)  # 新しい接続
        
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
        
        # ファイルを保存
        save_action = file_menu.addAction('Save')
        save_action.triggered.connect(self.save_data_file)
        save_action.setShortcut('Ctrl+S')
        
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

            # 解析モードをリセット
            self.analysis_mode = False

            # 解析なしで各ウィジェットを更新
            self.data_input.update_data(data['lap_data'], None)
            self.table_widget.update_data(data['lap_data'], None)
            # グラフ更新は行わない
            
            # 解析が必要な旨を通知
            QMessageBox.information(self, "Information", "Data loaded. Click 'Analyze Data' to perform analysis.")
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to process data: {str(e)}")

    def on_data_changed(self, data):
        """データが変更されたときの処理"""
        try:
            if not data:
                return
            
            # データが変更されたら解析モードをOFFに
            self.analysis_mode = False
            
            # 解析なしでテーブルデータのみ更新
            self.table_widget.update_data(data, None)
            # グラフは更新しない
            
            # 解析が必要であることを通知
            self.statusBar().showMessage("データが変更されました。解析するには'Analyze Data'ボタンをクリックしてください。", 5000)
        except Exception as e:
            print(f"Error updating data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to update data: {str(e)}")

    def on_analyze_requested(self, data):
        """データ解析リクエスト時の処理"""
        if not data:
            return
        
        try:
            # 解析モードをONに
            self.analysis_mode = True
            
            # 分析結果を取得
            analysis_results = self.analyzer.analyze_laps(data)
            
            # 各ウィジェットに分析結果を反映
            self.table_widget.update_data(data, analysis_results)
            self.graph_window.update_data(data, analysis_results)
            self.graph_window.show()  # グラフウィンドウを表示
            
            # 移動平均統計の計算
            moving_stats = self.analyzer.calculate_moving_statistics(data)
            self.stats_table.update_statistics(moving_stats)
            
            QMessageBox.information(self, "Information", "Analysis completed successfully.")
        except Exception as e:
            print(f"Error analyzing data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to analyze data: {str(e)}")

    def on_settings_updated(self, settings):
        """設定が更新されたときの処理"""
        # 設定変更前のセクター数を取得
        old_num_sectors = getattr(self, '_cached_num_sectors', None)
        if old_num_sectors is None:
            # 初回実行時はキャッシュがないので現在の値を使用
            old_num_sectors = self.config_manager.get_num_sectors()
            self._cached_num_sectors = old_num_sectors
            
        # 現在のセクター数を取得
        current_num_sectors = self.config_manager.get_num_sectors()
        
        # 設定変更を保存
        self.config_manager.save_config()
        
        # ライダーとタイヤ情報の更新
        self.update_riders_and_tires()
        
        # グラフウィンドウが存在する場合は更新
        if self.graph_window:
            self.graph_window.graph_widget.update_graph()
        
        # セクター数が変更された場合はメッセージを表示
        if old_num_sectors != current_num_sectors:
            QMessageBox.information(
                self,
                "セクター数の変更",
                f"セクター数が{old_num_sectors}から{current_num_sectors}に変更されました。\n"
                "この変更を完全に適用するには、アプリケーションの再起動が必要です。\n"
                "再起動後、テーブルやグラフに新しいセクター数が正しく反映されます。"
            )
            # 新しいセクター数をキャッシュ
            self._cached_num_sectors = current_num_sectors

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
            ' 2025 Takeshi Arai (Mushmans Racing Team)')

    def show_usage_guide(self):
        """使用方法ガイドを表示"""
        QMessageBox.information(self, '使用方法ガイド',
            '<h3>クイックスタートガイド</h3>'
            '<p><b>1. データの読み込み:</b></p>'
            '<ul>'
            '<li>「File > Open JSON」をクリックしてJSON形式のラップタイムデータを読み込む</li>'
            '<li>「File > Open CSV」をクリックしてCSV形式のラップタイムデータを読み込む</li>'
            '<li>初めて使用する場合は、サンプルデータを生成してお試しください</li>'
            '</ul>'
            '<p><b>2. データの確認:</b></p>'
            '<ul>'
            '<li>データ入力セクションではセッション情報を表示し、データの入力が可能です</li>'
            '<li>グラフセクションではラップタイムの様々な可視化が表示されます</li>'
            '<li>テーブルには各ライダーの詳細なラップデータが表示されます</li>'
            '<li>緑色の行は最速ラップを示します</li>'
            '<li>赤色の行は最遅ラップを示します</li>'
            '</ul>'
            '<p><b>3. データの分析:</b></p>'
            '<ul>'
            '<li>グラフタイプセレクタを使用して、異なる可視化を切り替えられます:</li>'
            '<li>- ラップタイム推移: ラップタイムの変化を表示</li>'
            '<li>- ラップタイム分布: ラップタイムの分布を表示</li>'
            '<li>- セクタータイム比較: セクターごとのパフォーマンスを比較</li>'
            '<li>- セクタータイム推移: セクタータイムの変化を表示</li>'
            '<li>- パフォーマンスレーダー: 総合的なパフォーマンスの可視化</li>'
            '</ul>'
            '<p><b>4. グラフの操作:</b></p>'
            '<ul>'
            '<li>ズーム: マウスホイールまたは矩形選択でズームイン</li>'
            '<li>パン: 右クリックドラッグでグラフを移動</li>'
            '<li>リセット: ホームボタンをクリックして元のビューに戻る</li>'
            '<li>保存: 保存ボタンをクリックしてグラフを画像として保存</li>'
            '</ul>'
            '<p><b>5. 設定:</b></p>'
            '<ul>'
            '<li>「Settings > Session Settings」でセッション情報を設定できます</li>'
            '<li>ライダーやタイヤの情報も管理できます</li>'
            '</ul>'
            '<p><b>6. データの入力・編集:</b></p>'
            '<ul>'
            '<li>データ入力ウィジェットでライダー、ラップ番号、タイム情報を入力</li>'
            '<li>「Add Lap」ボタンをクリックしてデータを追加</li>'
            '<li>タイヤタイプ、天候、路面温度などの走行条件も記録可能</li>'
            '</ul>'
        )

    def save_data_file(self):
        """ファイルを保存する"""
        # データ入力ウィジェットからデータを取得
        data = self.data_input.lap_data
        
        if not data:
            QMessageBox.warning(self, "警告", "保存するデータがありません。")
            return
            
        # 保存ファイル名を取得
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'ファイルを保存', '', 'データファイル (*)'
        )
        
        if not file_path:
            return  # ユーザーがキャンセルした場合
            
        # ファイル名から拡張子を除去（両方の形式で使用するため）
        file_base = file_path.rsplit('.', 1)[0] if '.' in file_path else file_path
        
        try:
            # セッション情報を取得
            session_info = self.config_manager.get_session_settings()
            print(f"Debug - MainWindow - Session Info from get_session_settings: {session_info}")
            
            # 設定から直接セッションデータを取得
            raw_session_data = self.config_manager.get_setting("session", "settings")
            print(f"Debug - MainWindow - Raw session data: {raw_session_data}")
            
            # JSONファイルとして保存
            json_file_path = file_base + '.json'
            json_saved = self.save_as_json(data, json_file_path, session_info)
            
            # CSVファイルとして保存 - 設定から直接トラック名と日付を取得
            track = ""
            date = ""
            
            if raw_session_data and isinstance(raw_session_data, dict):
                # session.sessionからcircuit（トラック名）と日付を取得
                session_subdata = raw_session_data.get("session", {})
                if isinstance(session_subdata, dict):
                    track = session_subdata.get("circuit", "")
                    date = session_subdata.get("date", "")
            
            print(f"Debug - MainWindow - Directly retrieved - Track: '{track}', Date: '{date}'")
            
            # トラック名と日付があれば付加する
            if track and date:
                # スペースをアンダースコアに置換
                track_formatted = track.replace(' ', '_')
                # ハイフンを除去（すでに日付にハイフンがない可能性あり）
                date_formatted = date.replace('-', '')
                csv_file_name = f"{file_base}_{track_formatted}_{date_formatted}.csv"
                print(f"Debug - MainWindow - Using formatted filename with track and date")
            else:
                csv_file_name = f"{file_base}.csv"
                print(f"Debug - MainWindow - Using base filename (no track/date)")
                
            print(f"Debug - MainWindow - CSV Filename: {csv_file_name}")
            csv_saved = self.save_as_csv(data, csv_file_name)
            
            if json_saved and csv_saved:
                QMessageBox.information(
                    self, 
                    "情報", 
                    f"データを保存しました。\nJSON: {json_file_path}\nCSV: {csv_file_name}"
                )
            elif json_saved:
                QMessageBox.information(
                    self, 
                    "情報", 
                    f"JSONデータのみ保存しました。\nJSON: {json_file_path}"
                )
            elif csv_saved:
                QMessageBox.information(
                    self, 
                    "情報", 
                    f"CSVデータのみ保存しました。\nCSV: {csv_file_name}"
                )
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            QMessageBox.critical(self, "エラー", f"データの保存に失敗しました: {str(e)}")
            
    def save_as_json(self, data, file_path, session_info=None):
        """データをJSON形式で保存"""
        try:
            # データをDataLoaderを使って保存
            formatted_data = {
                "session_info": session_info or {},
                "lap_data": self.data_loader._format_data_for_json(data)
            }
            
            # ファイルに保存
            self.data_loader.save_json(file_path, formatted_data)
            return True
        except ValueError as e:
            QMessageBox.critical(self, "エラー", f"JSONファイルの保存に失敗しました: {str(e)}")
            return False
        
    def save_as_csv(self, data, file_path):
        """データをCSV形式で保存"""
        try:
            # データをCSV形式に整形
            formatted_data = {
                'lap_data': data  # データローダーがこの形式を期待
            }
            
            # ファイルに保存
            self.data_loader.save_csv(file_path, formatted_data)
        except ValueError as e:
            QMessageBox.critical(self, "エラー", f"CSVファイルの保存に失敗しました: {str(e)}")
            return False
        return True