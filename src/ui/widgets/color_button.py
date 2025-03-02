"""
カラーボタンウィジェット
"""
from PyQt5.QtWidgets import QPushButton, QColorDialog
from PyQt5.QtGui import QColor

class ColorButton(QPushButton):
    """カラー選択可能なボタンウィジェット"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.color = None
        self.clicked.connect(self.pick_color)
        
    def pick_color(self):
        """カラーピッカーを表示し、色を選択する"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_color(color.name())
            
    def set_color(self, color):
        """ボタンの色をセット"""
        self.color = color
        self.setStyleSheet(f"background-color: {color}")
        
    def get_color(self):
        """現在設定されている色を取得"""
        return self.color
