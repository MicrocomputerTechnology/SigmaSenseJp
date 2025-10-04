import numpy as np

def _hsv_to_rgb(h, s, v):
    """簡易的なHSV to RGB変換"""
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

def identity(vector: np.ndarray) -> np.ndarray:
    """恒等射：ベクトルを何も変更しない"""
    return vector.copy()

def transform_for_rotation(vector: np.ndarray, dimension_loader) -> np.ndarray:
    """
    90度回転に対応するベクトル変換。
    中心にある対称的な図形の場合、多くの次元は不変のはず。
    アスペクト比は逆数になる。
    """
    new_vec = vector.copy()
    ar_index = dimension_loader.get_index('aspect_ratio')
    
    if ar_index is None:
        print("⚠️ Warning: 'aspect_ratio' dimension not found. Skipping rotation transform.")
        return new_vec

    # アスペクト比が0に近い場合は発散を防ぐ
    if new_vec[ar_index] > 1e-6:
        new_vec[ar_index] = 1.0 / new_vec[ar_index]
    
    return new_vec

def transform_for_red_tint(vector: np.ndarray, dimension_loader) -> np.ndarray:
    """
    赤色化に対応するベクトル変換 (HSV対応)。
    背景が白の場合、全体の明るさは少し低下する。
    暗い色には色は乗りにくい。
    """
    new_vec = vector.copy()
    hue_idx = dimension_loader.get_index('dominant_color_hue')
    sat_idx = dimension_loader.get_index('dominant_color_sat')
    val_idx = dimension_loader.get_index('dominant_color_val')
    brightness_idx = dimension_loader.get_index('brightness')

    if any(idx is None for idx in [hue_idx, sat_idx, val_idx, brightness_idx]):
        print("⚠️ Warning: Color/Brightness dimensions not found in vector_dimensions.json. Skipping red tint transform.")
        return new_vec

    # 仮説1: 色合いの追加は、全体の明るさを少し下げる
    new_vec[brightness_idx] *= 0.85

    # 仮説2: 元のオブジェクトが非常に暗い(明度が低い)場合、色はほとんど変化しない
    if new_vec[val_idx] < 0.1:
        return new_vec

    # 赤色化: 彩度を上げ、色相を赤(0.0)に近づける
    # 元の彩度を少し考慮に入れる
    new_vec[sat_idx] = min(1.0, new_vec[sat_idx] * 1.2 + 0.3)
    # 元の色相と赤(0)の中間あたりにシフト
    new_vec[hue_idx] = new_vec[hue_idx] * 0.3 # 0に近づける
        
    return new_vec

def transform_for_grayscale(vector: np.ndarray, dimension_loader) -> np.ndarray:
    """
    グレースケール化に対応するベクトル変換。
    理論的背景：グレースケール化は「色」レイヤーの情報をすべて失わせる変換である。
    したがって、予測されるベクトルは、元のベクトルから「色」レイヤーに属する次元の値を
    すべてゼロにしたものとなる。
    """
    new_vec = vector.copy()

    # dimension_loader を使って 'color' レイヤーに属する次元のインデックスを取得
    color_indices = dimension_loader.get_layer_indices('color')

    if not color_indices:
        print("⚠️ Warning: No 'color' layer dimensions found. Grayscale transform may be inaccurate.")
        return new_vec

    # 色関連の次元の値をすべて0にする
    for idx in color_indices:
        if idx < len(new_vec):
            new_vec[idx] = 0.0
    
    return new_vec
