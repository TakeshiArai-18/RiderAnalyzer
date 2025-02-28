from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

class TimeStatItem(QTableWidgetItem):
    """時間統計用のテーブルアイテム"""
    def __init__(self, time_value: float):
        super().__init__()
        self.time_value = time_value
        self.setText(self._format_time(time_value))
        self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # ソート用のデータを設定
        self.setData(Qt.UserRole, time_value)

    def _format_time(self, seconds: float) -> str:
        """時間を文字列にフォーマット（mm:ss.xxx）"""
        try:
            if seconds == 0 or seconds is None:
                return "--:--"

            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes:02d}:{remaining_seconds:06.3f}"
        except Exception as e:
            print(f"Error formatting time: {str(e)}")
            return "--:--"

class StdDevStatItem(QTableWidgetItem):
    """標準偏差用のテーブルアイテム"""
    def __init__(self, std_value: float):
        super().__init__()
        self.std_value = std_value
        self.setText(self._format_std(std_value))
        self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # ソート用のデータを設定
        self.setData(Qt.UserRole, std_value)

    def _format_std(self, value: float) -> str:
        """標準偏差を文字列にフォーマット（x.xxx）"""
        try:
            if value == 0 or value is None:
                return "--"
            return f"{value:.3f}"
        except Exception as e:
            print(f"Error formatting standard deviation: {str(e)}")
            return "--"
