import re
from typing import Union

class TimeConverter:
    def __init__(self):
        # 時間文字列のパターン
        self.time_patterns = [
            # "1:23.456" or "01:23.456"
            r'^(\d{1,2}):([0-5]\d)\.(\d{1,3})$',
            # "83.456" or "123.456"
            r'^(\d+)\.(\d{1,3})$',
            # "1:23" or "01:23"
            r'^(\d{1,2}):([0-5]\d)$',
            # "83" or "123"
            r'^(\d+)$'
        ]

    def string_to_seconds(self, time_str: str) -> float:
        """時間文字列を秒数に変換する

        Args:
            time_str (str): 変換する時間文字列

        Returns:
            float: 秒数

        Raises:
            ValueError: 無効な時間形式の場合
        """
        if not time_str or not isinstance(time_str, str):
            raise ValueError("Invalid time string")

        time_str = time_str.strip()
        if not time_str:
            raise ValueError("Empty time string")

        for pattern in self.time_patterns:
            match = re.match(pattern, time_str)
            if match:
                groups = match.groups()
                
                try:
                    if len(groups) == 3:  # "1:23.456"
                        minutes = int(groups[0])
                        seconds = int(groups[1])
                        ms = int(groups[2].ljust(3, '0'))
                        return minutes * 60 + seconds + ms / 1000
                    
                    elif len(groups) == 2:
                        if ':' in time_str:  # "1:23"
                            minutes = int(groups[0])
                            seconds = int(groups[1])
                            return minutes * 60 + seconds
                        else:  # "83.456"
                            seconds = int(groups[0])
                            ms = int(groups[1].ljust(3, '0'))
                            return seconds + ms / 1000
                    
                    else:  # "83"
                        return float(groups[0])
                
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Failed to convert time components: {str(e)}")

        raise ValueError(f"Invalid time format: {time_str}")

    def seconds_to_string(self, seconds: Union[int, float]) -> str:
        """秒数を時間文字列に変換する

        Args:
            seconds (Union[int, float]): 変換する秒数

        Returns:
            str: 時間文字列 (MM:SS.mmm)

        Raises:
            ValueError: 無効な秒数の場合
        """
        if not isinstance(seconds, (int, float)):
            raise ValueError("Invalid seconds value")

        try:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes:01d}:{remaining_seconds:06.3f}"
        except Exception as e:
            raise ValueError(f"Failed to convert seconds to string: {str(e)}")

    def is_valid_time_string(self, time_str: str) -> bool:
        """時間文字列が有効な形式かどうかを確認する

        Args:
            time_str (str): 確認する時間文字列

        Returns:
            bool: 有効な形式の場合はTrue
        """
        if not time_str or not isinstance(time_str, str):
            print(f"Debug: Invalid time string: '{time_str}' - Not a string or empty")
            return False

        time_str = time_str.strip()
        if not time_str:
            print(f"Debug: Invalid time string: Empty after stripping whitespace")
            return False

        # 時間形式の検証とデバッグ情報の出力
        match_results = [re.match(pattern, time_str) for pattern in self.time_patterns]
        if not any(match_results):
            print(f"Debug: Invalid time format: '{time_str}' - Does not match any pattern")
            return False
            
        return True