import numpy as np
from sklearn.metrics import mutual_info_score

def compute_entropy(vector):
    """
    ベクトルのエントロピーを計算する。
    値が正規化されていない場合でも、分布として扱う。
    """
    vec = np.array(vector)
    total = np.sum(vec)
    if total == 0:
        return 0.0
    probs = vec / total
    # ゼロや負の値をクリップしてlog計算のエラーを防ぐ
    probs = np.clip(probs, 1e-10, 1.0)
    entropy = -np.sum(probs * np.log2(probs))
    return round(float(entropy), 4)

def compute_sparsity(vector):
    """
    ベクトルのスパース度（ゼロ成分の割合）を計算する。
    """
    vec = np.array(vector)
    zero_count = np.sum(vec == 0)
    sparsity = zero_count / len(vec)
    return round(float(sparsity), 4)

def mutual_information(x, y, bins=32):
    """
    2つの連続値ベクトルの相互情報量を計算する。
    ベクトルを離散化してから計算する。
    """
    x = np.array(x)
    y = np.array(y)
    
    # NaNやinfを有限な値に置き換える
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]

    if len(x) == 0 or len(y) == 0 or len(x) != len(y):
        return 0.0

    # 最小値と最大値が同じ場合にbinsを調整
    min_x, max_x = np.min(x), np.max(x)
    min_y, max_y = np.min(y), np.max(y)

    x_bins = bins if min_x != max_x else 1
    y_bins = bins if min_y != max_y else 1

    # 離散化
    x_digitized = np.digitize(x, np.linspace(min_x, max_x, x_bins))
    y_digitized = np.digitize(y, np.linspace(min_y, max_y, y_bins))
    
    mi = mutual_info_score(x_digitized, y_digitized)
    return round(float(mi), 4)

def kl_divergence(p, q, epsilon=1e-10):
    """
    2つの確率分布ベクトル間のKLダイバージェンスを計算する。
    D_KL(P || Q)
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)

    # ゼロ除算を避けるために微小な値を加える
    p = p + epsilon
    q = q + epsilon
    
    # pとqを正規化
    p = p / np.sum(p)
    q = q / np.sum(q)

    # KLダイバージェンスの計算
    divergence = np.sum(p * np.log(p / q))
    return round(float(divergence), 4)