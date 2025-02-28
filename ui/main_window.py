from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                      QMenuBar, QMenu, QAction, QPushButton, QSplitter)
from PyQt5.QtCore import Qt

from src.ui.data_input_widget import DataInputWidget
from src.ui.graph_widget import GraphWidget
from src.ui.table_widget import TableWidget
from src.ui.settings_dialog import SettingsDialog
from src.app.analyzer import Analyzer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = Analyzer()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Lap Time Analyzer')
        self.setGeometry(100, 100, 1200, 800)

        self.create_menu_bar()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.data_input = DataInputWidget()
        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.show_settings)
        
        left_layout.addWidget(self.data_input)
        left_layout.addWidget(self.settings_button)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.graph_widget = GraphWidget()
        self.table_widget = TableWidget()
        
        right_layout.addWidget(self.graph_widget)
        right_layout.addWidget(self.table_widget)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        view_menu = menubar.addMenu('View')
        help_menu = menubar.addMenu('Help')
        
        open_action = QAction('Open', self)
        save_action = QAction('Save', self)
        exit_action = QAction('Exit', self)
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        exit_action.triggered.connect(self.close)

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def update_data(self, data):
        self.analyzer.process_data(data)
        self.graph_widget.update_graph(self.analyzer.get_graph_data())
        self.table_widget.update_table(self.analyzer.get_table_data())