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

            # セクター数を取得
            num_sectors = self.config.get_num_sectors()

            # ラップデータの処理
            processed_laps = []
            for i, lap in enumerate(lap_data):
                if not isinstance(lap, dict):
                    print(f"Warning: Skipping invalid lap data at index {i}")
                    continue

                try:
                    # 必須フィールドを動的に構築
                    required_fields = ['Rider', 'Lap', 'LapTime']
                    for j in range(1, num_sectors + 1):
                        required_fields.append(f'Sector{j}')
                    
                    # 必須フィールドの存在チェック
                    missing_fields = [field for field in required_fields if field not in lap]
                    if missing_fields:
                        print(f"Warning: Missing required fields in lap data at index {i}: {', '.join(missing_fields)}")
                        continue

                    # 基本データの処理
                    processed_lap = {
                        'Rider': str(lap['Rider']),
                        'Lap': int(lap['Lap']),
                        'LapTime': str(lap['LapTime']),
                    }
                    
                    # セクターデータの処理（動的）
                    for j in range(1, num_sectors + 1):
                        sector_key = f'Sector{j}'
                        processed_lap[sector_key] = str(lap.get(sector_key, ''))

                    # タイムデータの検証
                    invalid_time_fields = []
                    time_fields = ['LapTime']
                    for j in range(1, num_sectors + 1):
                        time_fields.append(f'Sector{j}')
                        
                    for field in time_fields:
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
                            'TrackTemp': str(conditions.get('track_temp', ''))
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
            # セクター数を取得
            num_sectors = self.config.get_num_sectors()
            
            # 必須カラムを動的に構築
            required_columns = ['Rider', 'Lap', 'LapTime']
            for i in range(1, num_sectors + 1):
                required_columns.append(f'Sector{i}')
            
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
                    }
                    
                    # セクターデータの処理（動的）
                    for j in range(1, num_sectors + 1):
                        sector_key = f'Sector{j}'
                        lap[sector_key] = str(row[sector_key])

                    # タイムデータの検証
                    time_fields = ['LapTime']
                    for j in range(1, num_sectors + 1):
                        time_fields.append(f'Sector{j}')
                        
                    if not all(self.time_converter.is_valid_time_string(lap[field]) for field in time_fields):
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

    def _format_data_for_json(self, data: List) -> List:
        """ラップデータをJSON形式用に整形する
        
        Args:
            data (List): ラップデータのリスト
            
        Returns:
            List: JSON形式用に整形されたデータ
            
        Raises:
            ValueError: データの形式が不正な場合
        """
        try:
            if not isinstance(data, list):
                raise ValueError("Invalid data format: expected a list of lap data")
            
            # セクター数を取得
            num_sectors = self.config.get_num_sectors()
                
            formatted_data = []
            
            for i, lap in enumerate(data):
                try:
                    if not isinstance(lap, dict):
                        print(f"Warning: Invalid lap data at index {i}: not a dictionary")
                        continue
                        
                    # 必須フィールドを動的に構築
                    required_fields = ['Rider', 'Lap', 'LapTime']
                    for j in range(1, num_sectors + 1):
                        required_fields.append(f'Sector{j}')
                    
                    # 必須フィールドの検証
                    missing_fields = [field for field in required_fields if field not in lap]
                    if missing_fields:
                        print(f"Warning: Missing required fields in lap data at index {i}: {', '.join(missing_fields)}")
                        continue
                        
                    # タイムデータの検証
                    invalid_time_fields = []
                    time_fields = ['LapTime']
                    for j in range(1, num_sectors + 1):
                        time_fields.append(f'Sector{j}')
                        
                    for field in time_fields:
                        if not self.time_converter.is_valid_time_string(lap[field]):
                            invalid_time_fields.append(f"{field}={lap[field]}")
                    
                    if invalid_time_fields:
                        print(f"Warning: Invalid time format in lap data at index {i}: {', '.join(invalid_time_fields)}")
                        continue
                    
                    # サンプル形式に合わせてデータを変換
                    formatted_lap = {
                        "Rider": lap['Rider'],
                        "Lap": lap['Lap'],
                        "LapTime": lap['LapTime'],
                    }
                    
                    # セクターデータの追加（動的）
                    for j in range(1, num_sectors + 1):
                        sector_key = f'Sector{j}'
                        formatted_lap[sector_key] = lap.get(sector_key, '')
                    
                    # コンディション情報の追加
                    formatted_lap["conditions"] = {
                        "tire": str(lap.get('TireType', '')),
                        "weather": str(lap.get('Weather', '')),
                        "track_temp": str(lap.get('TrackTemp', ''))
                    }
                    
                    formatted_data.append(formatted_lap)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Error processing lap data at index {i}: {str(e)}")
                    continue
            
            if not formatted_data:
                raise ValueError("No valid lap data could be formatted for JSON output")
                
            return formatted_data
        except Exception as e:
            raise ValueError(f"Failed to format data for JSON: {str(e)}")