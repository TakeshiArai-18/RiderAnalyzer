from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                           QComboBox, QLabel, QDialog, QLineEdit, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from utils.time_converter import TimeConverter

class DataInputWidget(QWidget):
    data_changed = pyqtSignal(list)  # データが変更されたときのシグナル
    analyze_requested = pyqtSignal(list)  # 解析リクエスト用の新しいシグナル

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.lap_data = []
        self.config_manager = config_manager
        self.time_converter = TimeConverter()  # タイム変換・検証用
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # ボタン配置用の水平レイアウト
        button_layout = QHBoxLayout()

        # データ操作ボタン
        self.add_lap_button = QPushButton('Add Lap')
        self.delete_data_button = QPushButton('Delete Data')

        # 解析ボタンを追加
        self.analyze_button = QPushButton('Analyze Data')
        self.analyze_button.setToolTip('Run analysis on current lap data')
        self.analyze_button.clicked.connect(self.analyze_clicked)

        # ボタンの接続
        self.add_lap_button.clicked.connect(self.add_lap_clicked)
        self.delete_data_button.clicked.connect(self.delete_data_clicked)

        # ボタンをレイアウトに追加
        button_layout.addWidget(self.add_lap_button)
        button_layout.addWidget(self.delete_data_button)
        button_layout.addWidget(self.analyze_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # ライダーとタイヤの選択セクション
        selection_layout = QHBoxLayout()
        
        # ライダー選択
        selection_layout.addWidget(QLabel("ライダー:"))
        self.rider_combo = QComboBox()
        self.update_riders_combo()  # ライダー一覧を更新
        selection_layout.addWidget(self.rider_combo)
        
        # タイヤ選択
        selection_layout.addWidget(QLabel("タイヤ:"))
        self.tire_combo = QComboBox()
        self.update_tires_combo()  # タイヤ一覧を更新
        selection_layout.addWidget(self.tire_combo)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        # テーブルウィジェット
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # コンディション情報を分割するため列数増加
        self.table.setHorizontalHeaderLabels([
            'Rider', 'Lap', 'Time', 'Sector1', 'Sector2', 'Sector3', 'タイヤ', '天候', '路面温度'
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def update_riders_combo(self):
        """ライダー選択コンボボックスを更新"""
        if not hasattr(self, 'rider_combo') or not self.config_manager:
            return
            
        self.rider_combo.clear()
        riders_list = self.config_manager.get_riders_list()
        
        for rider in riders_list:
            self.rider_combo.addItem(rider.get("name", ""))
            
        # デフォルトライダーを選択
        default_index = 0
        for i, rider in enumerate(riders_list):
            if rider.get("default", False):
                default_index = i
                break
        
        if self.rider_combo.count() > 0:
            self.rider_combo.setCurrentIndex(default_index)

    def update_tires_combo(self):
        """タイヤ選択コンボボックスを更新"""
        if not hasattr(self, 'tire_combo') or not self.config_manager:
            return
            
        self.tire_combo.clear()
        tires_list = self.config_manager.get_tires_list()
        
        for tire in tires_list:
            self.tire_combo.addItem(tire.get("name", ""))
            
        # デフォルトタイヤを選択
        default_index = 0
        for i, tire in enumerate(tires_list):
            if tire.get("default", False):
                default_index = i
                break
        
        if self.tire_combo.count() > 0:
            self.tire_combo.setCurrentIndex(default_index)

    def load_json_clicked(self):
        """JSONファイルを読み込むボタンがクリックされたときのハンドラ"""
        # MainWindowで処理するため、ここでは何もしない
        pass

    def load_csv_clicked(self):
        """CSVファイルを読み込むボタンがクリックされたときのハンドラ"""
        # MainWindowで処理するため、ここでは何もしない
        pass

    def add_lap_clicked(self):
        """ラップを追加するボタンがクリックされたときのハンドラ"""
        # ラップ追加ダイアログを表示
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Lap")
        # ヘルプボタンを非表示にする
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QFormLayout(dialog)
        
        # 現在選択されているライダーとタイヤを取得
        default_rider = self.rider_combo.currentText()
        default_tire = self.tire_combo.currentText()
        
        # 入力フィールド
        rider_combo = QComboBox()
        rider_combo.addItems([rider.get("name", "") for rider in self.config_manager.get_riders_list()])
        rider_combo.setCurrentText(default_rider)
        
        lap_number = QLineEdit()
        lap_time = QLineEdit()
        lap_time.setPlaceholderText("mm:ss.fff")
        sector1 = QLineEdit()
        sector1.setPlaceholderText("ss.fff")
        sector2 = QLineEdit()
        sector2.setPlaceholderText("ss.fff")
        sector3 = QLineEdit()
        sector3.setPlaceholderText("ss.fff")
        
        tire_combo = QComboBox()
        tire_combo.addItems([tire.get("name", "") for tire in self.config_manager.get_tires_list()])
        tire_combo.setCurrentText(default_tire)
        
        weather = QLineEdit()
        track_temp = QLineEdit()
        
        # 最新ラップデータを取得して自動入力
        latest_lap = self.get_latest_lap_for_rider(default_rider)
        if latest_lap:
            # 既存のラップがある場合は次のラップ番号を設定
            next_lap_number = latest_lap["Lap"] + 1
            lap_number.setText(str(next_lap_number))
        else:
            # 初めてのラップの場合は1を設定
            lap_number.setText("1")
        
        # セッション設定から天候と路面温度を取得
        session_settings = self.get_current_session_settings()
        if session_settings:
            if "Weather" in session_settings:
                weather.setText(session_settings["Weather"])
            if "TrackTemp" in session_settings:
                track_temp.setText(session_settings["TrackTemp"])
        
        # フォームにフィールドを追加
        layout.addRow("ライダー:", rider_combo)
        layout.addRow("ラップ番号:", lap_number)
        layout.addRow("ラップタイム:", lap_time)
        layout.addRow("セクター1:", sector1)
        layout.addRow("セクター2:", sector2)
        layout.addRow("セクター3:", sector3)
        layout.addRow("タイヤ:", tire_combo)
        layout.addRow("天候:", weather)
        layout.addRow("路面温度:", track_temp)
        
        # カスタムボタン（OKとキャンセルのみ）
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        # ダイアログを表示
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # データの検証
            validation_errors = []
            
            # ライダー名の検証
            if not rider_combo.currentText():
                validation_errors.append("ライダー名は必須です")
            
            # ラップ番号の検証
            try:
                lap_num = int(lap_number.text())
                if lap_num <= 0:
                    validation_errors.append("ラップ番号は正の整数を入力してください")
            except ValueError:
                validation_errors.append("ラップ番号は整数で入力してください")
                
            # ラップタイムの検証
            lap_time_str = lap_time.text().strip()
            if not lap_time_str:
                validation_errors.append("ラップタイムは必須です")
            elif not self.time_converter.is_valid_time_string(lap_time_str):
                validation_errors.append("ラップタイムは有効な形式で入力してください (例: 1:23.456)")
                
            # セクタータイムの検証
            for i, sector_time in enumerate([sector1.text().strip(), sector2.text().strip(), sector3.text().strip()], 1):
                if not sector_time:
                    validation_errors.append(f"セクター{i}タイムは必須です")
                elif not self.time_converter.is_valid_time_string(sector_time):
                    validation_errors.append(f"セクター{i}タイムは有効な形式で入力してください (例: 23.456)")
            
            # 検証エラーがある場合はメッセージを表示して処理を中断
            if validation_errors:
                error_message = "以下のエラーを修正してください:\n• " + "\n• ".join(validation_errors)
                QMessageBox.warning(self, "入力エラー", error_message)
                # ダイアログを再表示
                self.add_lap_clicked()
                return
                
            try:
                # データの作成
                new_lap = {
                    "Rider": rider_combo.currentText(),
                    "Lap": lap_num,
                    "LapTime": lap_time_str,
                    "Sector1": sector1.text().strip(),
                    "Sector2": sector2.text().strip(),
                    "Sector3": sector3.text().strip(),
                    "TireType": tire_combo.currentText(),
                    "Weather": weather.text().strip(),
                    "TrackTemp": track_temp.text().strip()
                }
                
                # セクタータイムの合計がラップタイムと一致するか確認（警告のみ）
                lap_time_ms = self.time_converter.time_string_to_milliseconds(lap_time_str)
                sector_total_ms = (
                    self.time_converter.time_string_to_milliseconds(sector1.text().strip()) +
                    self.time_converter.time_string_to_milliseconds(sector2.text().strip()) +
                    self.time_converter.time_string_to_milliseconds(sector3.text().strip())
                )
                
                # 許容誤差 (10ミリ秒)
                if abs(lap_time_ms - sector_total_ms) > 10:
                    discrepancy = abs(lap_time_ms - sector_total_ms) / 1000.0  # 秒単位に変換
                    warning = f"セクタータイムの合計とラップタイムに{discrepancy:.3f}秒の差異があります。\n" \
                              f"それでもこのデータを追加しますか？"
                    reply = QMessageBox.question(self, '確認', warning,
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    
                    if reply == QMessageBox.No:
                        # ダイアログを再表示
                        self.add_lap_clicked()
                        return
                
                # ラップデータに追加
                self.lap_data.append(new_lap)
                
                # テーブルを更新（解析結果なし）
                self.update_table()
                
                # データ変更シグナルを発行
                self.data_changed.emit(self.lap_data)
                
            except Exception as e:
                print(f"エラー: {str(e)}")
                QMessageBox.warning(self, "エラー", f"データの追加中にエラーが発生しました: {str(e)}")
                

    def delete_data_clicked(self):
        """データを削除するボタンがクリックされたときのハンドラ"""
        if not self.lap_data:
            return

        reply = QMessageBox.question(
            self, 'Confirm Delete',
            'Are you sure you want to delete all data?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.lap_data = []
            self.update_data(self.lap_data, None)
            self.data_changed.emit(self.lap_data)

    def update_data(self, laps, analysis_results=None):
        """データを更新し、テーブルに表示"""
        self.lap_data = laps
        self.table.setRowCount(len(laps))

        for row, lap in enumerate(laps):
            # 基本データの設定
            self.table.setItem(row, 0, QTableWidgetItem(str(lap['Rider'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(lap['Lap'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(lap['LapTime'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(lap['Sector1'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(lap['Sector2'])))
            self.table.setItem(row, 5, QTableWidgetItem(str(lap['Sector3'])))

            # コンディション情報を個別に設定
            self.table.setItem(row, 6, QTableWidgetItem(str(lap.get('TireType', ''))))
            self.table.setItem(row, 7, QTableWidgetItem(str(lap.get('Weather', ''))))
            self.table.setItem(row, 8, QTableWidgetItem(str(lap.get('TrackTemp', ''))))

            # 最速/最遅ラップの色付け
            if analysis_results and 'fastest_lap' in analysis_results and 'slowest_lap' in analysis_results:
                if lap == analysis_results['fastest_lap']:
                    for col in range(9):  # 列数を変更
                        self.table.item(row, col).setBackground(QColor(200, 255, 200))
                elif lap == analysis_results['slowest_lap']:
                    for col in range(9):  # 列数を変更
                        self.table.item(row, col).setBackground(QColor(255, 200, 200))

    def update_table(self):
        """テーブルウィジェットを更新"""
        self.table.setRowCount(len(self.lap_data))
        
        for row, lap in enumerate(self.lap_data):
            try:
                self.table.setItem(row, 0, QTableWidgetItem(str(lap.get("Rider", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(str(lap.get("Lap", ""))))
                self.table.setItem(row, 2, QTableWidgetItem(str(lap.get("LapTime", ""))))
                self.table.setItem(row, 3, QTableWidgetItem(str(lap.get("Sector1", ""))))
                self.table.setItem(row, 4, QTableWidgetItem(str(lap.get("Sector2", ""))))
                self.table.setItem(row, 5, QTableWidgetItem(str(lap.get("Sector3", ""))))
                self.table.setItem(row, 6, QTableWidgetItem(str(lap.get("TireType", ""))))
                self.table.setItem(row, 7, QTableWidgetItem(str(lap.get("Weather", ""))))
                self.table.setItem(row, 8, QTableWidgetItem(str(lap.get("TrackTemp", ""))))
            except Exception as e:
                print(f"テーブル更新エラー (行 {row}): {str(e)}")
                print(f"問題のデータ: {lap}")
                # エラーが発生しても処理を続行

    def get_latest_lap_for_rider(self, rider_name):
        """指定されたライダーの最新ラップデータを取得
        
        Args:
            rider_name (str): ライダー名
            
        Returns:
            dict or None: 最新ラップデータ。ラップがない場合はNone
        """
        rider_laps = [lap for lap in self.lap_data if lap["Rider"] == rider_name]
        if rider_laps:
            return max(rider_laps, key=lambda x: x["Lap"])
        return None

    def get_current_session_settings(self):
        """現在のセッション設定を取得
        
        Returns:
            dict or None: セッション設定。設定がない場合はNone
        """
        # config_managerからセッション設定を取得
        if self.config_manager:
            # 実際の実装に合わせて調整が必要かもしれません
            return self.config_manager.get_session_settings()
        return None

    def set_data(self, data):
        self.lap_data = data
        self.update_table()

    def analyze_clicked(self):
        """解析ボタンがクリックされたときのハンドラ"""
        if not self.lap_data:
            QMessageBox.warning(self, "Warning", "No data to analyze.")
            return
        
        # 解析リクエストを発行
        self.analyze_requested.emit(self.lap_data)