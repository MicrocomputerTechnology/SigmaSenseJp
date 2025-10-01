import cv2
import numpy as np

def analyze_lighting(img):
    """
    画像データ(NumPy array)の輝度分布と陰影強度を評価する。
    """
    if img is None:
        return {"brightness": 0.0, "shadow_intensity": 0.0}

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 輝度ヒストグラムから陰影領域の割合を計算
    # 輝度が低い（暗い）領域が多ければ陰影が強いと判断
    shadow_threshold = 80 # 閾値を少し調整
    shadow_pixels = np.sum(gray < shadow_threshold)
    total_pixels = gray.size
    
    # vector_generator.pyでのキー名'shadow_intensity'に合わせる
    shadow_intensity = shadow_pixels / total_pixels

    brightness = np.mean(gray) / 255.0
    
    return {
        "brightness": brightness,
        "shadow_intensity": shadow_intensity
    }
