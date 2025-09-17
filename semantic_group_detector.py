import numpy as np
from collections import Counter
import cv2

def detect_semantic_groups(regions):
    """
    同形状・類似サイズの対象群を検出し、その数と密度を返す。
    """
    if not regions or len(regions) < 2:
        return {"group_count": 0.0, "group_density": 0.0}

    # 形状（アスペクト比）とサイズ（面積）でグループ化キーを作成
    groups = []
    for r in regions:
        area = r["w"] * r["h"]
        if area == 0:
            continue
        # 面積はオーダーで丸める（例: 1234 -> 1200）
        area_order = 10**(np.floor(np.log10(area)) - 1)
        key = (
            round(r["w"] / r["h"], 1) if r["h"] > 0 else 0,
            round(area / area_order) * area_order
        )
        groups.append(key)
    
    if not groups:
        return {"group_count": 0.0, "group_density": 0.0}

    freq = Counter(groups)
    
    # 2つ以上でなければグループとはみなさない
    dominant_group = freq.most_common(1)[0]
    group_count = dominant_group[1] if dominant_group[1] >= 2 else 0

    if group_count == 0:
        return {"group_count": 0.0, "group_density": 0.0}

    # グループの密度を計算
    dominant_group_key = dominant_group[0]
    group_regions = [r for r, k in zip(regions, groups) if k == dominant_group_key]
    
    # グループを囲む最小の円の半径で密度を評価
    all_points = np.vstack([r['contour'] for r in group_regions])
    (x, y), radius = cv2.minEnclosingCircle(all_points)
    
    # 密度 = グループの合計面積 / 囲む円の面積
    group_area = sum(cv2.contourArea(r['contour']) for r in group_regions)
    enclosing_area = np.pi * radius**2
    density = group_area / enclosing_area if enclosing_area > 0 else 0.0

    # 0-1に正規化（グループ数を考慮）
    normalized_count = min(group_count / 10.0, 1.0) # 10個以上で1.0

    return {
        "group_count": normalized_count,
        "group_density": density
    }
