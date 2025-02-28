import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from app.analyzer import Analyzer

def main():
    app = QApplication(sys.argv)
    analyzer = Analyzer()
    window = MainWindow(analyzer)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()