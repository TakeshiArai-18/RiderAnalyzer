from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QComboBox, QPushButton, QColorDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        tab_widget.addTab(self.create_csv_tab(), "CSV Settings")
        tab_widget.addTab(self.create_graph_tab(), "Graph Settings")
        tab_widget.addTab(self.create_color_tab(), "Color Settings")
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(tab_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_csv_tab(self):
        widget = QGroupBox("CSV Column Settings")
        layout = QVBoxLayout()
        
        self.lap_time_col = QLineEdit(self.config_manager.get_setting("csv_columns", "lap_time"))
        self.sector1_col = QLineEdit(self.config_manager.get_setting("csv_columns", "sector1"))
        self.sector2_col = QLineEdit(self.config_manager.get_setting("csv_columns", "sector2"))
        self.sector3_col = QLineEdit(self.config_manager.get_setting("csv_columns", "sector3"))
        
        layout.addWidget(QLabel("Lap Time Column:"))
        layout.addWidget(self.lap_time_col)
        layout.addWidget(QLabel("Sector 1 Column:"))
        layout.addWidget(self.sector1_col)
        layout.addWidget(QLabel("Sector 2 Column:"))
        layout.addWidget(self.sector2_col)
        layout.addWidget(QLabel("Sector 3 Column:"))
        layout.addWidget(self.sector3_col)
        
        widget.setLayout(layout)
        return widget

    def create_graph_tab(self):
        widget = QGroupBox("Graph Settings")
        layout = QVBoxLayout()
        
        self.graph_type = QComboBox()
        self.graph_type.addItems(["Line", "Bar", "Scatter"])
        self.graph_type.setCurrentText(self.config_manager.get_setting("graph", "type"))
        
        self.show_grid = QComboBox()
        self.show_grid.addItems(["Yes", "No"])
        self.show_grid.setCurrentText(self.config_manager.get_setting("graph", "show_grid"))
        
        layout.addWidget(QLabel("Default Graph Type:"))
        layout.addWidget(self.graph_type)
        layout.addWidget(QLabel("Show Grid:"))
        layout.addWidget(self.show_grid)
        
        widget.setLayout(layout)
        return widget

    def create_color_tab(self):
        widget = QGroupBox("Color Settings")
        layout = QVBoxLayout()
        
        self.fastest_color = self.create_color_picker(
            "Fastest Lap Color",
            self.config_manager.get_setting("colors", "fastest")
        )
        self.slowest_color = self.create_color_picker(
            "Slowest Lap Color",
            self.config_manager.get_setting("colors", "slowest")
        )
        
        layout.addLayout(self.fastest_color)
        layout.addLayout(self.slowest_color)
        
        widget.setLayout(layout)
        return widget

    def create_color_picker(self, label, initial_color):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        
        color_button = QPushButton()
        color_button.setFixedSize(50, 25)
        color_button.setStyleSheet(f"background-color: {initial_color};")
        color_button.clicked.connect(lambda: self.pick_color(color_button))
        
        layout.addWidget(color_button)
        return layout

    def pick_color(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()};")

    def save_settings(self):
        self.config_manager.update_setting("csv_columns", {
            "lap_time": self.lap_time_col.text(),
            "sector1": self.sector1_col.text(),
            "sector2": self.sector2_col.text(),
            "sector3": self.sector3_col.text()
        })
        
        self.config_manager.update_setting("graph", {
            "type": self.graph_type.currentText(),
            "show_grid": self.show_grid.currentText()
        })
        
        self.config_manager.save_settings()
        self.accept()