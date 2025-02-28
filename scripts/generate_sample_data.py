import json
import random
from datetime import datetime

def generate_sector_time(base, variation):
    return round(base + random.uniform(-variation, variation), 3)

def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:.3f}" if minutes > 0 else f"{remaining_seconds:.3f}"

def generate_conditions(lap):
    # タイヤの選択（前半はソフト、後半はミディアム）
    tire = "soft" if lap <= 15 else "medium"
    
    # 天候は基本的にドライ、ただし20%の確率で曇り
    weather = "cloudy" if random.random() < 0.2 else "dry"
    
    # トラック温度は時間とともに上昇（26度から32度まで）
    base_temp = 26.0
    temp_increase = (32.0 - base_temp) * (lap / 30)
    track_temp = round(base_temp + temp_increase + random.uniform(-0.5, 0.5), 1)
    
    return {
        "tire": tire,
        "weather": weather,
        "track_temp": track_temp
    }

def generate_lap_data():
    # セッション情報
    session_info = {
        "track": "Suzuka Circuit",
        "date": "2024-03-15",
        "session_type": "Practice",
        "track_length": 5.807
    }

    lap_data = []
    
    # ライダーA: 安定した速いラップタイム
    base_times_a = {
        "sector1": 31.2,  # 基準タイム
        "sector2": 26.5,  # 基準タイム
        "sector3": 34.5   # 基準タイム
    }
    
    # ライダーB: 不安定だが時々速いラップ
    base_times_b = {
        "sector1": 31.8,  # やや遅い基準タイム
        "sector2": 27.0,
        "sector3": 35.0
    }
    
    # ライダーC: 徐々に向上
    base_times_c = {
        "sector1": 33.0,  # 最初は遅い
        "sector2": 28.0,
        "sector3": 35.5
    }

    # ライダーAのラップ生成（安定）
    for lap in range(1, 31):
        s1 = generate_sector_time(base_times_a["sector1"], 0.3)
        s2 = generate_sector_time(base_times_a["sector2"], 0.2)
        s3 = generate_sector_time(base_times_a["sector3"], 0.3)
        total = s1 + s2 + s3
        
        lap_data.append({
            "Rider": "Rider A",
            "Lap": lap,
            "LapTime": format_time(total),
            "Sector1": format_time(s1),
            "Sector2": format_time(s2),
            "Sector3": format_time(s3),
            "conditions": generate_conditions(lap)
        })

    # ライダーBのラップ生成（不安定）
    for lap in range(1, 31):
        # 時々速いラップを刻む（20%の確率）
        if random.random() < 0.2:
            s1 = generate_sector_time(base_times_a["sector1"], 0.2)  # 速いラップ
            s2 = generate_sector_time(base_times_a["sector2"], 0.2)
            s3 = generate_sector_time(base_times_a["sector3"], 0.2)
        else:
            s1 = generate_sector_time(base_times_b["sector1"], 0.8)  # 通常のラップ（ばらつき大）
            s2 = generate_sector_time(base_times_b["sector2"], 0.6)
            s3 = generate_sector_time(base_times_b["sector3"], 0.7)
        
        total = s1 + s2 + s3
        
        lap_data.append({
            "Rider": "Rider B",
            "Lap": lap,
            "LapTime": format_time(total),
            "Sector1": format_time(s1),
            "Sector2": format_time(s2),
            "Sector3": format_time(s3),
            "conditions": generate_conditions(lap)
        })

    # ライダーCのラップ生成（徐々に向上）
    improvement_rate = 0.05  # 1ラップごとの改善率
    for lap in range(1, 31):
        # 徐々に基準タイムを改善
        current_s1 = base_times_c["sector1"] - (improvement_rate * lap)
        current_s2 = base_times_c["sector2"] - (improvement_rate * lap)
        current_s3 = base_times_c["sector3"] - (improvement_rate * lap)
        
        # 改善後の基準タイムが速すぎないようにする
        current_s1 = max(current_s1, base_times_a["sector1"])
        current_s2 = max(current_s2, base_times_a["sector2"])
        current_s3 = max(current_s3, base_times_a["sector3"])
        
        s1 = generate_sector_time(current_s1, 0.4)
        s2 = generate_sector_time(current_s2, 0.4)
        s3 = generate_sector_time(current_s3, 0.4)
        total = s1 + s2 + s3
        
        lap_data.append({
            "Rider": "Rider C",
            "Lap": lap,
            "LapTime": format_time(total),
            "Sector1": format_time(s1),
            "Sector2": format_time(s2),
            "Sector3": format_time(s3),
            "conditions": generate_conditions(lap)
        })

    return {
        "session_info": session_info,
        "lap_data": lap_data
    }

# データ生成と保存
sample_data = generate_lap_data()
with open('../data/sample_data.json', 'w', encoding='utf-8') as f:
    json.dump(sample_data, f, indent=2, ensure_ascii=False)
