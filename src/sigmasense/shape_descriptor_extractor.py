import cv2
import numpy as np

def compute_area_ratio(contour, img_area):
    area = cv2.contourArea(contour)
    return area / img_area if img_area > 0 else 0.0

def compute_symmetry(contour):
    # モーメントから重心を計算
    moments = cv2.moments(contour)
    if moments["m00"] == 0:
        return 0.0
    cx = int(moments["m10"] / moments["m00"])

    # 重心で左右に分割して比較するのは複雑なので、
    # バウンディングボックスの縦横比の対称性で代用する
    x, y, w, h = cv2.boundingRect(contour)
    # 縦長の形状と横長の形状を区別し、どちらも1から離れるほど非対称とする
    ratio = w/h if h > 0 else 1.0
    symmetry_score = 1.0 - abs(1.0 - ratio) if ratio <= 1 else 1.0 - abs(1.0 - 1.0/ratio)
    return max(0, symmetry_score) # 負にならないように

def extract_shape_features(contours, img_shape):
    if not contours:
        return {
            "contour_complexity": 0.0,
            "area_ratio": 0.0,
            "aspect_ratio": 0.0,
            "symmetry": 0.0,
            # Add Hu Moments with default 0.0 values
            **{f"hu_moment_{i+1}": 0.0 for i in range(7)}
        }

    img_area = img_shape[0] * img_shape[1]
    largest_contour = max(contours, key=cv2.contourArea)
    
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Calculate Hu Moments
    moments = cv2.moments(largest_contour)
    hu_moments = []
    if moments["m00"] != 0: # Avoid division by zero for normalized moments
        hu_moments = cv2.HuMoments(moments).flatten()
    else:
        hu_moments = np.zeros(7) # If m00 is zero, contour is just a point or line, Hu moments are undefined

    # 輪郭の複雑さ（頂点数で近似）
    perimeter = cv2.arcLength(largest_contour, True)
    epsilon = 0.02 * perimeter
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    # 0-1に正規化（最大50頂点と仮定）
    complexity = min(len(approx) / 50.0, 1.0)

    features = {
        "contour_complexity": complexity,
        "area_ratio": compute_area_ratio(largest_contour, img_area),
        "aspect_ratio": w / h if h > 0 else 0.0,
        "symmetry": compute_symmetry(largest_contour)
    }

    # Add all 7 Hu Moments
    for i, hu_m in enumerate(hu_moments):
        features[f"hu_moment_{i+1}"] = float(hu_m)

    return features
