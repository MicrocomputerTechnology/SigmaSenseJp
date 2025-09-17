import numpy as np
import cv2

def extract_spatial_relations(regions, img_shape):
    """
    領域間の空間的関係性を抽出し、代表値を辞書として返す。
    """
    if not regions:
        return {
            "centroid_x": 0.0,
            "centroid_y": 0.0,
            "inclusion_relation": 0.0
        }

    h, w = img_shape[:2]

    # --- 全体の重心を計算 ---
    all_contours = [r['contour'] for r in regions]
    cx, cy = 0, 0
    if all_contours:
        combined_contours = np.vstack(all_contours)
        moments = cv2.moments(combined_contours)
        if moments["m00"] != 0:
            cx = moments["m10"] / moments["m00"]
            cy = moments["m01"] / moments["m00"]

    # --- 包含関係を計算 ---
    inclusions = []
    if len(regions) > 1:
        for i, r1 in enumerate(regions):
            for j, r2 in enumerate(regions):
                if i == j:
                    continue
                # r2がr1に完全に含まれているか
                if (r1["x"] <= r2["x"] and r1["y"] <= r2["y"] and
                    r1["x"] + r1["w"] >= r2["x"] + r2["w"] and
                    r1["y"] + r1["h"] >= r2["y"] + r2["h"]):
                    inclusions.append(1.0)

    mean_inclusion = np.mean(inclusions) if inclusions else 0.0

    return {
        "centroid_x": cx / w if w > 0 else 0.0,  # 0-1に正規化
        "centroid_y": cy / h if h > 0 else 0.0,  # 0-1に正規化
        "inclusion_relation": mean_inclusion
    }
