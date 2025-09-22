import cv2
import numpy as np

def extract_structure_features(image_path):
    """
    対象物の領域群を抽出する。
    距離変換とwatershedアルゴリズムを用いて、重なり合ったオブジェクトの分離を試みる。
    各領域は {"x": ..., "y": ..., "w": ..., "h": ...} の形式。
    """
    img = cv2.imread(image_path)
    if img is None:
        return []
    if np.std(img) < 5: # Threshold for solid color
        h, w, _ = img.shape
        return [{"x": 0, "y": 0, "w": w, "h": h}]


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # ノイズ除去
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # 確実な背景領域の特定
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # 確実な前景領域の特定
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

    # 不明な領域の特定
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # マーカーのラベリング
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # watershedアルゴリズムの適用
    markers = cv2.watershed(img, markers)
    
    regions = []
    # markersには背景(-1)と各オブジェクト(1, 2, ...)のラベルが含まれる
    unique_labels = np.unique(markers)
    for label in unique_labels:
        # 背景や未定義領域は無視
        if label <= 0:
            continue
        
        # ラベルに対応するマスクを作成
        mask = np.zeros(gray.shape, dtype="uint8")
        mask[markers == label] = 255
        
        # マスクから輪郭を見つける
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 最大の輪郭（オブジェクト全体）のバウンディングボックスを取得
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            regions.append({"x": x, "y": y, "w": w, "h": h})

    return regions
