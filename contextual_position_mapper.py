import numpy as np

def map_contextual_position(region, img_shape):
    """
    対象領域の重心から、中心からの距離と中心性の判定を辞書で返す。
    """
    if region is None:
        return {"dist_from_center": 1.0, "is_central": 0.0}

    h, w = img_shape[:2]
    img_center_x, img_center_y = w / 2, h / 2
    
    # 領域の重心
    cx = region["x"] + region["w"] / 2
    cy = region["y"] + region["h"] / 2
    
    # 中心からの距離を計算し、画像の対角線の長さで正規化
    dist = np.sqrt((cx - img_center_x)**2 + (cy - img_center_y)**2)
    max_dist = np.sqrt(w**2 + h**2) / 2
    normalized_dist = dist / max_dist if max_dist > 0 else 0.0
    
    # 中心領域にあるかの判定（中心から20%以内など）
    is_central_flag = 1.0 if normalized_dist < 0.2 else 0.0

    return {
        "dist_from_center": normalized_dist,
        "is_central": is_central_flag
    }
