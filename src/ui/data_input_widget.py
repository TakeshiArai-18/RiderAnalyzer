from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                           QComboBox, QLabel, QDialog, QLineEdit, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor

class DataInputWidget(QWidget):
    data_changed = pyqtSignal(list)  # データが変更されたときのシグナル

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.lap_data = []
        self.config_manager = config_manager
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # ボタン配置用の水平レイアウト
        button_layout = QHBoxLayout()

        # データ操作ボタン
        self.load_json_button = QPushButton('Load JSON')
        self.load_csv_button = QPushButton('Load CSV')
        self.add_lap_button = QPushButton('Add Lap')
        self.delete_data_button = QPushButton('Delete Data')

        # ボタンの接続
        self.load_json_button.clicked.connect(self.load_json_clicked)
        self.load_csv_button.clicked.connect(self.load_csv_clicked)
        self.add_lap_button.clicked.connect(self.add_lap_clicked)
        self.delete_data_button.clicked.connect(self.delete_data_clicked)

        # ボタンをレイアウトに追加
        button_layout.addWidget(self.load_json_button)
        button_layout.addWidget(self.load_csv_button)
        button_layout.addWidget(self.add_lap_button)
        button_layout.addWidget(self.delete_data_button)
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
        sector1 = QLineEdit()
        sector2 = QLineEdit()
        sector3 = QLineEdit()
        
        tire_combo = QComboBox()
        tire_combo.addItems([tire.get("name", "") for tire in self.config_manager.get_tires_list()])
        tire_combo.setCurrentText(default_tire)
        
        weather = QLineEdit()
        track_temp = QLineEdit()
        
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
        
        # ボタン
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        # ダイアログを表示
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            try:
                # 入力データの検証
                lap_num = int(lap_number.text())
                new_lap = {
                    "Rider": rider_combo.currentText(),
                    "Lap": lap_num,
                    "LapTime": lap_time.text(),
                    "Sector1": sector1.text(),
                    "Sector2": sector2.text(),
                    "Sector3": sector3.text(),
                    "TireType": tire_combo.currentText(),
                    "Weather": weather.text(),
                    "TrackTemp": track_temp.text()
                }
                
                # ラップデータに追加
                self.lap_data.append(new_lap)
                
                # テーブルを更新
                self.update_data(self.lap_data)
                
                # 変更シグナルを発行
                self.data_changed.emit(self.lap_data)
                
            except ValueError:
                QMessageBox.warning(self, "入力エラー", "ラップ番号には整数を入力してください。")

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
            self.update_data(self.lap_data)
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
            if analysis_results:
                if lap == analysis_results['fastest_lap']:
                    for col in range(9):  # 列数を変更
                        self.table.item(row, col).setBackground(QColor(200, 255, 200))
                elif lap == analysis_results['slowest_lap']:
                    for col in range(9):  # 列数を変更
                        self.table.item(row, col).setBackground(QColor(255, 200, 200))