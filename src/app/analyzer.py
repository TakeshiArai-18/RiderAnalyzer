import numpy as np
from typing import Dict, List, Optional, Union
from utils.time_converter import TimeConverter
from app.config_manager import ConfigManager

class LapTimeAnalyzer:
    def __init__(self, data_loader, config_manager: ConfigManager):
        """Initialize LapTimeAnalyzer
        
        Args:
            data_loader: データローダーインスタンス
            config_manager: 設定マネージャーインスタンス
        """
        self.time_converter = TimeConverter()
        self.config_manager = config_manager
        self.window_size = 3  # 移動平均のウィンドウサイズ

    def analyze_laps(self, laps: List[Dict]) -> Dict:
        """ラップデータを分析する"""
        try:
            if not laps:
                return self._create_empty_analysis()

            # 時間データを数値に変換
            processed_laps = []
            for lap in laps:
                try:
                    processed_lap = lap.copy()
                    processed_lap['time'] = self.time_converter.string_to_seconds(lap['LapTime'])
                    processed_lap['sector1'] = self.time_converter.string_to_seconds(lap['Sector1'])
                    processed_lap['sector2'] = self.time_converter.string_to_seconds(lap['Sector2'])
                    processed_lap['sector3'] = self.time_converter.string_to_seconds(lap['Sector3'])
                    processed_laps.append(processed_lap)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Skipping invalid lap data: {str(e)}")
                    continue

            if not processed_laps:
                return self._create_empty_analysis()

            # 最速/最遅ラップを特定
            fastest_lap = min(processed_laps, key=lambda x: x['time'])
            slowest_lap = max(processed_laps, key=lambda x: x['time'])

            # ライダーごとの統計を計算
            riders = set(lap['Rider'] for lap in processed_laps)
            rider_stats = {}
            
            for rider in riders:
                rider_laps = [lap for lap in processed_laps if lap['Rider'] == rider]
                if rider_laps:
                    times = [lap['time'] for lap in rider_laps]
                    rider_stats[rider] = {
                        'best_lap': min(rider_laps, key=lambda x: x['time']),
                        'worst_lap': max(rider_laps, key=lambda x: x['time']),
                        'avg_time': np.mean(times),
                        'std_dev': np.std(times) if len(times) > 1 else 0,
                        'lap_count': len(rider_laps)
                    }

            # セクターごとの統計を計算
            sector_stats = self._calculate_sector_stats(processed_laps)

            return {
                'fastest_lap': fastest_lap,
                'slowest_lap': slowest_lap,
                'rider_stats': rider_stats,
                'sector_stats': sector_stats,
                'total_laps': len(processed_laps)
            }

        except Exception as e:
            print(f"Error in analyze_laps: {str(e)}")
            return self._create_empty_analysis()

    def _calculate_sector_stats(self, laps: List[Dict]) -> Dict:
        """セクターごとの統計を計算する"""
        try:
            if not laps:
                return {}

            sectors = ['sector1', 'sector2', 'sector3']
            stats = {}

            for sector in sectors:
                sector_times = [lap[sector] for lap in laps if sector in lap]
                if sector_times:
                    stats[sector] = {
                        'best': min(sector_times),
                        'worst': max(sector_times),
                        'avg': np.mean(sector_times),
                        'std_dev': np.std(sector_times) if len(sector_times) > 1 else 0
                    }

            return stats
        except Exception as e:
            print(f"Error in _calculate_sector_stats: {str(e)}")
            return {}

    def _create_empty_analysis(self) -> Dict:
        """空の分析結果を作成する"""
        return {
            'fastest_lap': None,
            'slowest_lap': None,
            'rider_stats': {},
            'sector_stats': {},
            'total_laps': 0
        }

    def get_rider_stats(self, rider: str, laps: List[Dict], analysis_results=None) -> Optional[Dict]:
        """特定のライダーの統計を取得する"""
        try:
            if analysis_results is None:
                analysis = self.analyze_laps(laps)
            else:
                analysis = analysis_results
            return analysis['rider_stats'].get(rider)
        except Exception as e:
            print(f"Error in get_rider_stats: {str(e)}")
            return None

    def get_sector_stats(self, laps: List[Dict], analysis_results=None) -> Dict:
        """セクター統計を取得する"""
        try:
            if analysis_results is None:
                analysis = self.analyze_laps(laps)
            else:
                analysis = analysis_results
            return analysis['sector_stats']
        except Exception as e:
            print(f"Error in get_sector_stats: {str(e)}")
            return {}

    def calculate_moving_statistics(self, laps: List[Dict]) -> Dict:
        """移動平均と標準偏差を含む詳細な統計情報を計算（既存の分析機能に影響を与えない追加機能）

        Args:
            laps: 分析対象のラップデータ

        Returns:
            Dict: {
                'rider_name': {
                    'lap_time': {
                        'moving_avg': float,  # 秒単位
                        'std_dev': float      # 秒単位
                    },
                    'sectors': {
                        'sector1': {'moving_avg': float, 'std_dev': float},
                        'sector2': {'moving_avg': float, 'std_dev': float},
                        'sector3': {'moving_avg': float, 'std_dev': float}
                    }
                }
            }
        """
        try:
            if not laps:
                return {}

            stats = {}
            riders = set(lap['Rider'] for lap in laps)

            for rider in riders:
                rider_laps = [lap for lap in laps if lap['Rider'] == rider]
                if rider_laps:
                    stats[rider] = {
                        'lap_time': self._calculate_moving_stats([
                            self.time_converter.string_to_seconds(lap['LapTime'])
                            for lap in rider_laps
                        ]),
                        'sectors': {
                            'sector1': self._calculate_moving_stats([
                                self.time_converter.string_to_seconds(lap['Sector1'])
                                for lap in rider_laps
                            ]),
                            'sector2': self._calculate_moving_stats([
                                self.time_converter.string_to_seconds(lap['Sector2'])
                                for lap in rider_laps
                            ]),
                            'sector3': self._calculate_moving_stats([
                                self.time_converter.string_to_seconds(lap['Sector3'])
                                for lap in rider_laps
                            ])
                        }
                    }

            return stats
        except Exception as e:
            print(f"Error calculating moving statistics: {str(e)}")
            return {}

    def _calculate_moving_stats(self, times: List[float]) -> Dict[str, float]:
        """移動平均と標準偏差を計算

        Args:
            times: 時間データのリスト（秒単位）

        Returns:
            Dict[str, float]: {
                'moving_avg': float,  # 移動平均（秒）
                'std_dev': float      # 標準偏差（秒）
            }
        """
        try:
            if not times:
                return {'moving_avg': 0.0, 'std_dev': 0.0}

            # 移動平均の計算
            if len(times) >= self.window_size:
                recent_times = times[-self.window_size:]
            else:
                recent_times = times

            return {
                'moving_avg': np.mean(recent_times),
                'std_dev': np.std(recent_times) if len(recent_times) > 1 else 0.0
            }
        except Exception as e:
            print(f"Error calculating moving stats: {str(e)}")
            return {'moving_avg': 0.0, 'std_dev': 0.0}

    def set_window_size(self, size: int):
        """移動平均のウィンドウサイズを設定

        Args:
            size: ウィンドウサイズ（正の整数）
        """
        if size > 0:
            self.window_size = size