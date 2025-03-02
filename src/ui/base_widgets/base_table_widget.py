"""
Base Table Widget Module
テーブルウィジェットの基底クラスを提供します。
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QLabel, QHBoxLayout)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class BaseTableWidget(QWidget):
    """テーブルウィジェットの基底クラス"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.setup_table()
        
    def setup_table(self):
        """テーブルの基本設定（子クラスでオーバーライド可能）"""
        self.table = QTableWidget()
        self.main_layout.addWidget(self.table)
        
        # 共通テーブル設定
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
    def configure_header(self, headers, resizable_columns=None, fixed_width_columns=None):
        """ヘッダーの設定
        
        Args:
            headers (list): カラムヘッダー名のリスト
            resizable_columns (list, optional): リサイズ可能にするカラムインデックスのリスト
            fixed_width_columns (dict, optional): 固定幅にするカラムと幅の辞書 {カラムインデックス: 幅}
        """
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        header = self.table.horizontalHeader()
        
        # リサイズ可能な列の設定
        if resizable_columns:
            for col in resizable_columns:
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        # 固定幅の列の設定
        if fixed_width_columns:
            for col, width in fixed_width_columns.items():
                header.setSectionResizeMode(col, QHeaderView.Fixed)
                self.table.setColumnWidth(col, width)
                
    def clear_table(self):
        """テーブルをクリア"""
        self.table.setRowCount(0)
        
    def apply_color_to_row(self, row, color):
        """行全体に色を適用
        
        Args:
            row (int): 色を適用する行のインデックス
            color (QColor): 適用する色
        """
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)


class TableColorUtils:
    """テーブルの色付けに関するユーティリティ"""
    @staticmethod
    def get_best_time_color():
        """最速タイム用の色を返す"""
        return QColor(200, 255, 200)  # 薄い緑
        
    @staticmethod
    def get_worst_time_color():
        """最遅タイム用の色を返す"""
        return QColor(255, 200, 200)  # 薄い赤
        
    @staticmethod
    def apply_color_to_item(item, color):
        """アイテムに色を適用"""
        if item:
            item.setBackground(color)
