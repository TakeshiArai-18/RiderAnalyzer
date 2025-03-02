from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer
from .graph_widget import GraphWidget

class GraphWindow(QMainWindow):
    """グラフ表示用の別ウィンドウ"""
    def __init__(self, analyzer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RiderCal - Graph View")
        self.resize(1200, 800)
        
        # メインウィジェットとレイアウト設定
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # GraphWidgetを追加
        self.graph_widget = GraphWidget(analyzer, self)
        self.main_layout.addWidget(self.graph_widget)
        
        # 閉じるボタンのためのレイアウト
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        # スペーサーを追加して右寄せにする
        self.button_layout.addStretch()
        
        # 閉じるボタン
        self.close_button = QPushButton("閉じる")
        self.close_button.clicked.connect(self.hide)  # ウィンドウを非表示にする
        self.button_layout.addWidget(self.close_button)
    
    def set_position_from_parent(self):
        """親ウィンドウと同じ位置に配置"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            # 親ウィンドウと同じ位置に配置
            self.setGeometry(parent_geometry.x(), parent_geometry.y(), 
                            self.width(), self.height())
    
    def update_data(self, data, analysis_results=None):
        """データを更新"""
        self.graph_widget.update_data(data, analysis_results)
        
        # 解析結果がある場合のみウィンドウを表示する（設定で有効な場合）
        if analysis_results and self.graph_widget.analyzer.config_manager.get_setting("app_settings", "show_graph_window"):
            # 親ウィンドウと同じ位置に配置
            self.set_position_from_parent()
            self.show()
            self.activateWindow()
            self.raise_()
    
    def resizeEvent(self, event):
        """ウィンドウリサイズ時にグラフを再描画"""
        super().resizeEvent(event)
        # サイズ変更後にキャンバス全体を再描画
        QTimer.singleShot(100, self._configure_and_redraw)
    
    def _configure_and_redraw(self):
        """設定とリサイズを行う専用メソッド"""
        if hasattr(self, 'graph_widget') and hasattr(self.graph_widget, 'data') and self.graph_widget.data is not None:
            self.graph_widget._configure_figure_size_and_layout()
            self.graph_widget.canvas.draw_idle()
