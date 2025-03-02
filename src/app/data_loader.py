import json
import pandas as pd
from typing import Dict, List, Union
from app.config_manager import ConfigManager
from utils.time_converter import TimeConverter

class DataLoader:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.time_converter = TimeConverter()

    def load_json(self, file_path: str) -> Dict:
        """JSONファイルを読み込み、データを処理する"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._process_json_data(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            raise ValueError(f"Failed to load JSON file: {str(e)}")

    def load_csv(self, file_path: str) -> Dict:
        """CSVファイルを読み込み、データを処理する"""
        try:
            df = pd.read_csv(file_path)
            return self._process_csv_data(df)
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {str(e)}")

    def _process_json_data(self, data: Dict) -> Dict:
        """JSONデータを処理して標準形式に変換する"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON data format: root must be an object")

            # セッション情報の取得
            session_info = data.get('session_info', {})
            if not isinstance(session_info, dict):
                raise ValueError("Invalid session_info format")

            lap_data = data.get('lap_data', [])
            if not isinstance(lap_data, list):
                raise ValueError("Invalid lap_data format: must be an array")

            # ラップデータの処理
            processed_laps = []
            for i, lap in enumerate(lap_data):
                if not isinstance(lap, dict):
                    print(f"Warning: Skipping invalid lap data at index {i}")
                    continue

                try:
                    # 基本データの検証と変換
                    required_fields = ['Rider', 'Lap', 'LapTime', 'Sector1', 'Sector2', 'Sector3']
                    missing_fields = [field for field in required_fields if field not in lap]
                    if missing_fields:
                        print(f"Warning: Missing required fields in lap data at index {i}: {', '.join(missing_fields)}")
                        continue

                    processed_lap = {
                        'Rider': str(lap['Rider']),
                        'Lap': int(lap['Lap']),
                        'LapTime': str(lap['LapTime']),
                        'Sector1': str(lap['Sector1']),
                        'Sector2': str(lap['Sector2']),
                        'Sector3': str(lap['Sector3'])
                    }

                    # タイムデータの検証
                    invalid_time_fields = []
                    for field in ['LapTime', 'Sector1', 'Sector2', 'Sector3']:
                        if not self.time_converter.is_valid_time_string(processed_lap[field]):
                            invalid_time_fields.append(f"{field}={processed_lap[field]}")
                    
                    if invalid_time_fields:
                        print(f"Warning: Invalid time format in lap data at index {i}: {', '.join(invalid_time_fields)}")
                        continue

                    # コンディション情報の処理
                    conditions = lap.get('conditions', {})
                    if isinstance(conditions, dict):
                        processed_lap.update({
                            'TireType': str(conditions.get('tire', '')),
                            'Weather': str(conditions.get('weather', '')),
                            'TrackTemp': conditions.get('track_temp', '')
                        })

                    processed_laps.append(processed_lap)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Error processing lap data at index {i}: {str(e)}")
                    continue

            if not processed_laps:
                error_details = "Please check if:\n" \
                               "1. The file contains valid lap data with required fields (Rider, Lap, LapTime, Sector1, Sector2, Sector3)\n" \
                               "2. The time format is valid (e.g. 1:23.456, 83.456, 1:23, or 83)"
                raise ValueError(f"No valid lap data found. {error_details}")

            return {
                'session_info': session_info,
                'lap_data': processed_laps
            }
        except Exception as e:
            raise ValueError(f"Failed to process JSON data: {str(e)}")

    def _process_csv_data(self, df: pd.DataFrame) -> Dict:
        """CSVデータを処理して標準形式に変換する"""
        try:
            required_columns = ['Rider', 'Lap', 'LapTime', 'Sector1', 'Sector2', 'Sector3']
            
            # 必要なカラムが存在するか確認
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # データを処理
            processed_laps = []
            for i, row in df.iterrows():
                try:
                    # 基本データの検証と変換
                    lap = {
                        'Rider': str(row['Rider']),
                        'Lap': int(row['Lap']),
                        'LapTime': str(row['LapTime']),
                        'Sector1': str(row['Sector1']),
                        'Sector2': str(row['Sector2']),
                        'Sector3': str(row['Sector3'])
                    }

                    # タイムデータの検証
                    if not all(self.time_converter.is_valid_time_string(lap[field]) 
                             for field in ['LapTime', 'Sector1', 'Sector2', 'Sector3']):
                        print(f"Warning: Invalid time format in row {i}")
                        continue

                    # オプションのコンディション情報
                    for field in ['TireType', 'Weather', 'TrackTemp']:
                        if field in df.columns:
                            lap[field] = str(row[field]) if pd.notna(row[field]) else ''

                    processed_laps.append(lap)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Error processing row {i}: {str(e)}")
                    continue

            if not processed_laps:
                raise ValueError("No valid lap data found")
            
            return {
                'session_info': {},  # CSVにはセッション情報がない
                'lap_data': processed_laps
            }
        except Exception as e:
            raise ValueError(f"Failed to process CSV data: {str(e)}")

    def save_json(self, file_path: str, data: Dict) -> None:
        """JSONデータをファイルに保存する"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save JSON file: {str(e)}")

    def save_csv(self, file_path: str, data: Dict) -> None:
        """CSVデータをファイルに保存する"""
        try:
            df = pd.DataFrame(data['lap_data'])
            df.to_csv(file_path, index=False)
        except Exception as e:
            raise ValueError(f"Failed to save CSV file: {str(e)}")