import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        # configディレクトリのパスを取得
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_dir = os.path.join(base_dir, "config")
        
        # configディレクトリが存在しない場合は作成
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 設定ファイルのパスを設定
        self.config_file = os.path.join(config_dir, config_file)
        self.config = self._load_default_config()
        self._load_config()

    def _load_default_config(self) -> Dict[str, Any]:
        return {
            "csv_settings": {
                "lap_time_column": "LapTime",
                "sector1_column": "Sector1",
                "sector2_column": "Sector2",
                "sector3_column": "Sector3",
                "rider_column": "Rider"
            },
            "app_settings": {
                "show_graph_window": True,  # グラフウィンドウを表示するかどうか
                "num_sectors": 3  # セクター数のデフォルト値
            },
            "graph_settings": {
                "line_color": "#1f77b4",
                "marker_size": 6,
                "grid": True,
                "title_font_size": 14,
                "axis_font_size": 12,
                "line_width": 1.5,
                "marker_style": "o",
                "line_style": "-",
                "show_grid": True,
                "lap_trend_window_size": 3,  # ラップタイムトレンドの移動平均ウィンドウサイズ
                "radar_window_size": 3,      # レーダーチャートの移動平均ウィンドウサイズ
                "radar_alpha": 0.2           # レーダーチャートの標準偏差表示の透明度
            },
            "color_settings": {
                "fastest_lap": "#00ff00",
                "slowest_lap": "#ff0000",
                "normal_lap": "#ffffff"
            },
            "display_settings": {
                "show_grid": True,
                "show_statistics": True,
                "decimal_places": 3
            },
            "stats_table_settings": {
                "time_stats": {
                    "fastest": "#C8FFC8",  # 薄い緑
                    "slowest": "#FFC8C8",  # 薄い赤
                    "enabled": True        # 色付けの有効/無効
                },
                "std_dev_stats": {
                    "highest": "#FFE8C8",  # 薄いオレンジ
                    "lowest": "#C8E8FF",   # 薄い青
                    "enabled": True        # 色付けの有効/無効
                }
            },
            "riders_settings": {
                "riders_list": [
                    {
                        "id": "rider1",
                        "name": "Default Rider",
                        "bike": "Default Bike",
                        "color": "#1f77b4",
                        "default": True
                    }
                ]
            },
            "tires_settings": {
                "tires_list": [
                    {
                        "id": "tire1",
                        "name": "ソフト",
                        "description": "ソフトコンパウンド",
                        "color": "#FFC0CB",
                        "default": True
                    },
                    {
                        "id": "tire2",
                        "name": "ミディアム",
                        "description": "ミディアムコンパウンド",
                        "color": "#FFFF00",
                        "default": False
                    },
                    {
                        "id": "tire3",
                        "name": "ハード",
                        "description": "ハードコンパウンド",
                        "color": "#C0C0C0",
                        "default": False
                    }
                ]
            }
        }

    def _load_config(self) -> None:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_setting(self, section: str, key: str) -> Any:
        return self.config.get(section, {}).get(key)

    def update_setting(self, section: str, key: str, value: Any) -> None:
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def set_setting(self, section: str, key: str, value: Any) -> None:
        """update_settingのエイリアス（後方互換性のため）"""
        self.update_setting(section, key, value)

    def reset_to_default(self) -> None:
        self.config = self._load_default_config()
        
    # ライダー管理用のメソッド
    def get_riders_list(self):
        """登録済みのライダーリストを取得"""
        return self.get_setting("riders_settings", "riders_list") or []

    def add_rider(self, rider_data):
        """新しいライダーを追加"""
        riders_list = self.get_riders_list()
        
        # IDの生成（既存のIDとの重複を避ける）
        existing_ids = set(rider.get("id") for rider in riders_list)
        new_id = f"rider{len(riders_list) + 1}"
        while new_id in existing_ids:
            new_id = f"rider{int(new_id[5:]) + 1}"
        
        rider_data["id"] = new_id
        riders_list.append(rider_data)
        
        self.update_setting("riders_settings", "riders_list", riders_list)
        self.save_config()
        
        # 後方互換性のため、古い形式でも色を保存
        if "name" in rider_data and "color" in rider_data:
            self.set_setting("graph", f"rider_color_{rider_data['name']}", rider_data["color"])
        
        return new_id

    def update_rider(self, rider_id, rider_data):
        """既存のライダー情報を更新"""
        riders_list = self.get_riders_list()
        
        # 指定されたIDのライダーを検索
        for i, rider in enumerate(riders_list):
            if rider.get("id") == rider_id:
                # 古い名前を取得（後方互換性のため）
                old_name = rider.get("name")
                
                # データを更新（IDは変更しない）
                rider_data["id"] = rider_id
                riders_list[i] = rider_data
                
                self.update_setting("riders_settings", "riders_list", riders_list)
                self.save_config()
                
                # 後方互換性のため、古い形式での色設定も更新
                if "name" in rider_data and "color" in rider_data:
                    # 名前が変わった場合は古い設定を削除
                    if old_name != rider_data["name"] and old_name:
                        self.remove_setting("graph", f"rider_color_{old_name}")
                    # 新しい名前で設定
                    self.set_setting("graph", f"rider_color_{rider_data['name']}", rider_data["color"])
                
                return True
        
        return False  # ライダーが見つからない

    def delete_rider(self, rider_id):
        """ライダーを削除"""
        riders_list = self.get_riders_list()
        
        # 指定されたIDのライダーを検索
        for i, rider in enumerate(riders_list):
            if rider.get("id") == rider_id:
                # 後方互換性のため、古い形式の設定も削除
                name = rider.get("name")
                if name:
                    self.remove_setting("graph", f"rider_color_{name}")
                
                # リストから削除
                riders_list.pop(i)
                
                self.update_setting("riders_settings", "riders_list", riders_list)
                self.save_config()
                return True
        
        return False  # ライダーが見つからない

    # タイヤ管理用のメソッド
    def get_tires_list(self):
        """登録済みのタイヤリストを取得"""
        return self.get_setting("tires_settings", "tires_list") or []

    def add_tire(self, tire_data):
        """新しいタイヤを追加"""
        tires_list = self.get_tires_list()
        
        # IDの生成
        existing_ids = set(tire.get("id") for tire in tires_list)
        new_id = f"tire{len(tires_list) + 1}"
        while new_id in existing_ids:
            new_id = f"tire{int(new_id[4:]) + 1}"
        
        tire_data["id"] = new_id
        tires_list.append(tire_data)
        
        self.update_setting("tires_settings", "tires_list", tires_list)
        self.save_config()
        return new_id

    def update_tire(self, tire_id, tire_data):
        """既存のタイヤ情報を更新"""
        tires_list = self.get_tires_list()
        
        for i, tire in enumerate(tires_list):
            if tire.get("id") == tire_id:
                # データを更新（IDは変更しない）
                tire_data["id"] = tire_id
                tires_list[i] = tire_data
                
                self.update_setting("tires_settings", "tires_list", tires_list)
                self.save_config()
                return True
        
        return False  # タイヤが見つからない

    def delete_tire(self, tire_id):
        """タイヤを削除"""
        tires_list = self.get_tires_list()
        
        for i, tire in enumerate(tires_list):
            if tire.get("id") == tire_id:
                tires_list.pop(i)
                
                self.update_setting("tires_settings", "tires_list", tires_list)
                self.save_config()
                return True
        
        return False  # タイヤが見つからない

    def get_rider_color(self, rider_name):
        """ライダーの色を取得するメソッド（新旧両方の設定に対応）"""
        # 1. 新しい設定形式から探す
        riders_list = self.get_setting("riders_settings", "riders_list") or []
        for rider in riders_list:
            if rider.get("name") == rider_name:
                return rider.get("color")
        
        # 2. 古い設定形式から探す（後方互換性）
        return self.get_setting("graph", f"rider_color_{rider_name}")

    def remove_setting(self, section, key):
        """設定を削除する"""
        if section in self.config and key in self.config[section]:
            del self.config[section][key]
            
    def migrate_to_new_format(self):
        """既存の設定を新しい形式に移行する"""
        # 既存のライダー情報を確認
        current_session = self.get_setting("session", "settings")
        known_riders = self.get_setting("graph", "known_riders") or []
        
        riders_list = self.get_riders_list()
        
        # 既存のライダーが新形式に存在しない場合は追加
        if current_session and isinstance(current_session, dict):
            rider_info = current_session.get("rider", {})
            rider_name = rider_info.get("name")
            
            if rider_name and not any(r.get("name") == rider_name for r in riders_list):
                # 既存のライダー色を取得
                rider_color = self.get_setting("graph", f"rider_color_{rider_name}")
                
                # 新形式でライダーを追加
                new_rider = {
                    "name": rider_name,
                    "bike": rider_info.get("bike", ""),
                    "color": rider_color or "#1f77b4",
                    "default": True
                }
                self.add_rider(new_rider)
        
        # known_ridersにあるライダーも追加
        for rider_name in known_riders:
            if not any(r.get("name") == rider_name for r in self.get_riders_list()):
                rider_color = self.get_setting("graph", f"rider_color_{rider_name}")
                
                new_rider = {
                    "name": rider_name,
                    "bike": "",
                    "color": rider_color or "#1f77b4",
                    "default": False
                }
                self.add_rider(new_rider)
                
    def get_session_settings(self):
        """現在のセッション設定を取得
        
        Returns:
            dict: セッション設定。トラック、日付、セッションタイプ、天候、路面温度などの情報を含む
        """
        session_data = self.get_setting("session", "settings")
        print(f"Debug - Config Manager - Raw session data: {session_data}")
        
        if not session_data or not isinstance(session_data, dict):
            # セッション設定がない場合はデフォルト値を返す
            return {
                "track": "Unknown Track",
                "date": "",
                "session_type": "Practice",
                "Weather": "",
                "TrackTemp": ""
            }
        
        # セッション情報の構造を詳細にデバッグ
        print(f"Debug - Config Manager - Session data keys: {session_data.keys()}")
        
        # セッション情報がJSON構造に基づいて正しく取得
        session_info = session_data.get("session", {})
        
        # session.circuitからトラック名を取得（優先）、次にトップレベルのtrackキーを確認
        track = ""
        if session_info and isinstance(session_info, dict):
            track = session_info.get("circuit", "")
        
        # 上記で取得できなければsession_dataのトップレベルのtrackキーを確認
        if not track or track.strip() == "":
            track = session_data.get("track", "")
            
        if not track or track.strip() == "":
            track = "Unknown Track"
        
        # session.dateから日付を取得（優先）、次にトップレベルのdateキーを確認
        date = ""
        if session_info and isinstance(session_info, dict):
            date = session_info.get("date", "")
            
        # 上記で取得できなければsession_dataのトップレベルのdateキーを確認
        if not date or date.strip() == "":
            date = session_data.get("date", "")
            
        if not date or date.strip() == "":
            date = ""
        
        print(f"Debug - Config Manager - Session info: {session_info}")
        print(f"Debug - Config Manager - Track: '{track}', Date: '{date}'")
        
        # 条件情報とセッション基本情報を取得
        conditions = session_data.get("conditions", {})
        
        result = {
            "track": track,
            "date": date,
            "session_type": session_data.get("session_type", "Practice"),
            "Weather": conditions.get("weather", ""),
            "TrackTemp": str(conditions.get("track_temp", ""))
        }
        
        print(f"Debug - Config Manager - Processed session data: {result}")
        return result

    def get_num_sectors(self) -> int:
        """セクター数を取得する

        Returns:
            int: セクター数（デフォルトは3）
        """
        num_sectors = self.get_setting("app_settings", "num_sectors")
        if not isinstance(num_sectors, int) or num_sectors < 1:
            # デフォルト値を返す
            return 3
        return num_sectors

    def set_num_sectors(self, num_sectors: int) -> None:
        """セクター数を設定する

        Args:
            num_sectors (int): 設定するセクター数（1以上の整数）
        """
        if not isinstance(num_sectors, int) or num_sectors < 1:
            raise ValueError("Number of sectors must be a positive integer")
        self.update_setting("app_settings", "num_sectors", num_sectors)
        self.save_config()