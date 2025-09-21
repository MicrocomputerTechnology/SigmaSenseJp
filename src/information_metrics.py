import numpy as np
from scipy.stats import wasserstein_distance
from sklearn.metrics import mutual_info_score
import math

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

def compute_kl_divergence(p, q):
    """
    2つのベクトル（確率分布とみなす）間のKLダイバージェンスを計算する。
    D_KL(P || Q)
    """
    p_vec = np.asarray(p, dtype=float)
    q_vec = np.asarray(q, dtype=float)

    # ゼロや負の値が含まれていないことを確認
    if np.any(p_vec < 0) or np.any(q_vec < 0):
        raise ValueError("入力ベクトルに負の値を含めることはできません。")

    # 合計が0の場合は、空の分布として0を返す
    if np.sum(p_vec) == 0 or np.sum(q_vec) == 0:
        return 0.0

    # 確率分布に正規化
    p_norm = p_vec / np.sum(p_vec)
    q_norm = q_vec / np.sum(q_vec)

    # ゼロ割りを避けるための微小値を追加
    p_norm = np.where(p_norm == 0, 1e-10, p_norm)
    q_norm = np.where(q_norm == 0, 1e-10, q_norm)

    divergence = np.sum(p_norm * np.log2(p_norm / q_norm))
    return round(float(divergence), 4)

def compute_wasserstein_distance(p, q):
    """
    2つの1Dベクトル（値の分布とみなす）間のWasserstein距離を計算する。
    """
    p_vec = np.asarray(p, dtype=float)
    q_vec = np.asarray(q, dtype=float)

    # 負の値チェック
    if np.any(p_vec < 0) or np.any(q_vec < 0):
        raise ValueError("入力ベクトルに負の値を含めることはできません。")

    # 空のベクトルは0を返す
    if p_vec.size == 0 or q_vec.size == 0:
        return 0.0

    distance = wasserstein_distance(p_vec, q_vec)
    return round(float(distance), 4)

def compute_mutual_information(labels_true, labels_pred):
    """
    2つのラベル配列間の相互情報量を計算する。
    """
    # mutual_info_scoreは内部でnp.logを使用（自然対数）
    mi_score_nats = mutual_info_score(labels_true, labels_pred)
    # bits（2を底とする対数）に変換
    mi_score_bits = mi_score_nats / math.log(2)
    return round(float(mi_score_bits), 4)
