import csv
from typing import Dict, List
from utils.time_converter import TimeConverter

class StatsExporter:
    def __init__(self):
        self.time_converter = TimeConverter()

    def export_to_csv(self, stats_data: Dict, filepath: str) -> bool:
        """統計データをCSVファイルにエクスポート

        Args:
            stats_data: LapTimeAnalyzer.calculate_moving_statistics()の戻り値
            filepath: 出力先のファイルパス

        Returns:
            bool: エクスポートの成功/失敗
        """
        try:
            headers = [
                "Rider",
                "Lap Time (Avg)", "Lap Time SD",
                "Sector1 (Avg)", "Sector1 SD",
                "Sector2 (Avg)", "Sector2 SD",
                "Sector3 (Avg)", "Sector3 SD"
            ]

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for rider, stats in stats_data.items():
                    row = [
                        rider,
                        self._format_time(stats['lap_time']['moving_avg']),
                        self._format_time(stats['lap_time']['std_dev']),
                        self._format_time(stats['sectors']['sector1']['moving_avg']),
                        self._format_time(stats['sectors']['sector1']['std_dev']),
                        self._format_time(stats['sectors']['sector2']['moving_avg']),
                        self._format_time(stats['sectors']['sector2']['std_dev']),
                        self._format_time(stats['sectors']['sector3']['moving_avg']),
                        self._format_time(stats['sectors']['sector3']['std_dev'])
                    ]
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False

    def export_to_markdown(self, stats_data: Dict, filepath: str) -> bool:
        """統計データをMarkdownファイルにエクスポート

        Args:
            stats_data: LapTimeAnalyzer.calculate_moving_statistics()の戻り値
            filepath: 出力先のファイルパス

        Returns:
            bool: エクスポートの成功/失敗
        """
        try:
            headers = [
                "Rider",
                "Lap Time (Avg)", "Lap Time SD",
                "Sector1 (Avg)", "Sector1 SD",
                "Sector2 (Avg)", "Sector2 SD",
                "Sector3 (Avg)", "Sector3 SD"
            ]

            with open(filepath, 'w') as f:
                # ヘッダー行
                f.write("| " + " | ".join(headers) + " |\n")
                # 区切り行
                f.write("|" + "|".join(["---" for _ in headers]) + "|\n")

                # データ行
                for rider, stats in stats_data.items():
                    row = [
                        rider,
                        self._format_time(stats['lap_time']['moving_avg']),
                        self._format_time(stats['lap_time']['std_dev']),
                        self._format_time(stats['sectors']['sector1']['moving_avg']),
                        self._format_time(stats['sectors']['sector1']['std_dev']),
                        self._format_time(stats['sectors']['sector2']['moving_avg']),
                        self._format_time(stats['sectors']['sector2']['std_dev']),
                        self._format_time(stats['sectors']['sector3']['moving_avg']),
                        self._format_time(stats['sectors']['sector3']['std_dev'])
                    ]
                    f.write("| " + " | ".join(row) + " |\n")

            return True
        except Exception as e:
            print(f"Error exporting to Markdown: {str(e)}")
            return False

    def _format_time(self, seconds: float) -> str:
        """時間を文字列にフォーマット（mm:ss.xxx）"""
        try:
            if seconds == 0:
                return "--:--"

            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes:02d}:{remaining_seconds:06.3f}"
        except Exception as e:
            print(f"Error formatting time: {str(e)}")
            return "--:--"
