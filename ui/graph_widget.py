from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                                 QPushButton, QFrame)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np

class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        controls_layout = QHBoxLayout()
        
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems([
            "Lap Time Trend",
            "Sector Time Comparison",
            "Performance Distribution",
            "Rider Comparison"
        ])
        self.graph_type_combo.currentIndexChanged.connect(self.updateGraph)
        
        self.settings_button = QPushButton("Graph Settings")
        self.settings_button.clicked.connect(self.showGraphSettings)
        
        controls_layout.addWidget(self.graph_type_combo)
        controls_layout.addWidget(self.settings_button)
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)

    def setAnalyzer(self, analyzer):
        self.analyzer = analyzer
        self.updateGraph()

    def updateGraph(self):
        if not self.analyzer:
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        graph_type = self.graph_type_combo.currentText()
        
        if graph_type == "Lap Time Trend":
            self.plotLapTimeTrend(ax)
        elif graph_type == "Sector Time Comparison":
            self.plotSectorComparison(ax)
        elif graph_type == "Performance Distribution":
            self.plotPerformanceDistribution(ax)
        elif graph_type == "Rider Comparison":
            self.plotRiderComparison(ax)
            
        self.canvas.draw()

    def plotLapTimeTrend(self, ax):
        data = self.analyzer.getLapTimeData()
        sns.lineplot(data=data, ax=ax)
        ax.set_title("Lap Time Trend")
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time (seconds)")

    def plotSectorComparison(self, ax):
        data = self.analyzer.getSectorData()
        sns.boxplot(data=data, ax=ax)
        ax.set_title("Sector Time Comparison")
        ax.set_xlabel("Sector")
        ax.set_ylabel("Time (seconds)")

    def plotPerformanceDistribution(self, ax):
        data = self.analyzer.getPerformanceData()
        sns.histplot(data=data, ax=ax)
        ax.set_title("Performance Distribution")
        ax.set_xlabel("Lap Time (seconds)")
        ax.set_ylabel("Frequency")

    def plotRiderComparison(self, ax):
        data = self.analyzer.getRiderComparisonData()
        sns.barplot(data=data, ax=ax)
        ax.set_title("Rider Comparison")
        ax.set_xlabel("Rider")
        ax.set_ylabel("Average Lap Time (seconds)")

    def showGraphSettings(self):
        # Graph settings dialog implementation
        pass