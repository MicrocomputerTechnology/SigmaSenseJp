import cv2
import numpy as np

def extract_average_color(img):
    """
    画像の前景オブジェクトの平均色をHSV色空間で抽出し、
    色相(hue)、彩度(saturation)、明度(value)を返す。
    オブジェクトの移動に対して頑健なように、バウンディングボックスで切り抜いてから計算する。
    """
    if img is None:
        return {"dominant_color_hue": 0.0, "dominant_color_sat": 0.0, "dominant_color_val": 0.0}

    # グレースケールに変換し、大津の二値化で前景マスクを生成
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # マスクから輪郭を抽出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return {"dominant_color_hue": 0.0, "dominant_color_sat": 0.0, "dominant_color_val": 0.0}

    # 最大の輪郭を見つけて、そのバウンディングボックスを取得
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # バウンディングボックスで元画像とマスクを切り抜く
    img_cropped = img[y:y+h, x:x+w]
    mask_cropped = mask[y:y+h, x:x+w]

    # 前景ピクセルが存在するかチェック
    if cv2.countNonZero(mask_cropped) == 0:
        return {"dominant_color_hue": 0.0, "dominant_color_sat": 0.0, "dominant_color_val": 0.0}

    # BGRからHSVに変換
    hsv_img_cropped = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2HSV)
    
    # 切り抜いた領域でマスクを使って前景領域の平均HSV値を計算
    mean_hsv = cv2.mean(hsv_img_cropped, mask=mask_cropped)

    # 0-1の範囲に正規化して返す
    return {
        "dominant_color_hue": mean_hsv[0] / 179.0,
        "dominant_color_sat": mean_hsv[1] / 255.0,
        "dominant_color_val": mean_hsv[2] / 255.0
    }
