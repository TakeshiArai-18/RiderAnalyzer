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
        self.delete_data_button = QPushButton('Delete Selected')
        self.delete_data_button.setToolTip('Delete selected lap data rows')

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
        
        # 行選択モードを設定
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 行単位での選択
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)  # 複数選択可能
        
        # セルが編集されたときのシグナルを接続
        self.table.cellChanged.connect(self.on_cell_changed)
        
        layout.addWidget(self.table)

        self.setLayout(layout)
        
        # 編集中フラグ (cellChangedイベントの再帰呼び出しを防止)
        self.is_editing = False

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
        """選択されたデータを削除するボタンがクリックされたときのハンドラ"""
        if not self.lap_data:
            QMessageBox.information(self, "情報", "削除するデータがありません。")
            return

        # 選択された行のインデックスを取得（ユニークな行のみ）
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, "情報", "削除する行を選択してください。")
            return

        # 選択された行の番号を取得（重複なし）
        selected_rows = set(index.row() for index in selected_indexes)
        
        # 確認ダイアログを表示
        reply = QMessageBox.question(
            self, '削除の確認',
            f'選択された {len(selected_rows)} 行のデータを削除してもよろしいですか？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 選択された行のデータを特定して削除（逆順で処理して混乱を避ける）
            rows_to_delete = sorted(selected_rows, reverse=True)
            for row in rows_to_delete:
                # テーブルに表示されている順序と実際のデータの順序が一致することを前提としています
                if row < len(self.lap_data):
                    del self.lap_data[row]
            
            # テーブルを更新
            self.update_table()
            
            # データ変更シグナルを発行
            self.data_changed.emit(self.lap_data)
            
            QMessageBox.information(self, "情報", f"{len(selected_rows)} 行のデータが削除されました。")

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

    def on_cell_changed(self, row, column):
        """セルの値が変更されたときの処理"""
        # 編集中の場合は何もしない（再帰呼び出し防止）
        if self.is_editing or row >= len(self.lap_data):
            return
            
        self.is_editing = True
        
        try:
            # 変更されたセルの値を取得
            cell_value = self.table.item(row, column).text().strip()
            
            # 列ごとの検証と処理
            is_valid = True
            error_message = ""
            
            if column == 0:  # Rider
                if not cell_value:
                    is_valid = False
                    error_message = "ライダー名は必須です"
                self.lap_data[row]['Rider'] = cell_value
                
            elif column == 1:  # Lap
                try:
                    lap_num = int(cell_value)
                    if lap_num <= 0:
                        is_valid = False
                        error_message = "ラップ番号は正の整数である必要があります"
                    else:
                        self.lap_data[row]['Lap'] = lap_num
                except ValueError:
                    is_valid = False
                    error_message = "ラップ番号は整数である必要があります"
                    
            elif column in [2, 3, 4, 5]:  # LapTime, Sector1, Sector2, Sector3
                column_names = {2: 'LapTime', 3: 'Sector1', 4: 'Sector2', 5: 'Sector3'}
                if not cell_value:
                    is_valid = False
                    error_message = f"{column_names[column]}は必須です"
                elif not self.time_converter.is_valid_time_string(cell_value):
                    is_valid = False
                    error_message = f"{column_names[column]}は有効な時間形式である必要があります"
                else:
                    self.lap_data[row][column_names[column]] = cell_value
                    
                    # セクタータイムの合計とラップタイムの整合性チェック
                    if column in [2, 3, 4, 5] and all(self.table.item(row, c) and self.table.item(row, c).text().strip() for c in [2, 3, 4, 5]):
                        lap_time = self.table.item(row, 2).text().strip()
                        sector1 = self.table.item(row, 3).text().strip()
                        sector2 = self.table.item(row, 4).text().strip()
                        sector3 = self.table.item(row, 5).text().strip()
                        
                        if all(self.time_converter.is_valid_time_string(t) for t in [lap_time, sector1, sector2, sector3]):
                            lap_time_ms = self.time_converter.time_string_to_milliseconds(lap_time)
                            sector_total_ms = (
                                self.time_converter.time_string_to_milliseconds(sector1) +
                                self.time_converter.time_string_to_milliseconds(sector2) +
                                self.time_converter.time_string_to_milliseconds(sector3)
                            )
                            
                            # 許容誤差 (10ミリ秒)
                            if abs(lap_time_ms - sector_total_ms) > 10:
                                discrepancy = abs(lap_time_ms - sector_total_ms) / 1000.0  # 秒単位に変換
                                warning = f"セクタータイムの合計とラップタイムに{discrepancy:.3f}秒の差異があります。"
                                QMessageBox.warning(self, '警告', warning)
                    
            elif column == 6:  # TireType
                self.lap_data[row]['TireType'] = cell_value
                
            elif column == 7:  # Weather
                self.lap_data[row]['Weather'] = cell_value
                
            elif column == 8:  # TrackTemp
                # 数値として解釈可能か確認（オプション）
                if cell_value and not cell_value.isdigit() and not (cell_value.replace('.', '', 1).isdigit() and cell_value.count('.') <= 1):
                    # 警告を表示するが、値は許可する（文字列として保存）
                    QMessageBox.warning(self, '警告', "路面温度は数値であることが望ましいです")
                self.lap_data[row]['TrackTemp'] = cell_value
            
            # 検証失敗時は元の値に戻す
            if not is_valid:
                QMessageBox.warning(self, "入力エラー", error_message)
                # テーブルを更新して元の値に戻す
                self.update_table()
            else:
                # データ変更シグナルを発行
                self.data_changed.emit(self.lap_data)
                
        except Exception as e:
            print(f"セル編集エラー: {e}")
            QMessageBox.warning(self, "エラー", f"データの編集中にエラーが発生しました: {str(e)}")
            self.update_table()  # エラー時はテーブルを元に戻す
        
        finally:
            self.is_editing = False