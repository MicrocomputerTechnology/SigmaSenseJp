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

def compute_wasserstein_distance(u_values, v_values, u_weights=None, v_weights=None):
    """
    2つの分布間のWasserstein距離を計算する。
    u_values, v_valuesは分布のサポート（値）、u_weights, v_weightsは対応する確率（重み）。
    """
    u_values = np.asarray(u_values, dtype=float)
    v_values = np.asarray(v_values, dtype=float)

    # 負の値チェックはscipy関数に任せるか、別途厳密に行う

    # 空のベクトルは0を返す
    if u_values.size == 0 or v_values.size == 0:
        return 0.0

    distance = wasserstein_distance(u_values, v_values, u_weights=u_weights, v_weights=v_weights)
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

def to_probability_distribution(data, bins=10):
    """
    数値データの1D配列を確率分布に変換する（ヒストグラムを使用）。
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)

    if data.size == 0:
        return np.array([]), np.array([])

    # ヒストグラムを作成し、度数分布を得る
    hist, bin_edges = np.histogram(data, bins=bins, density=False)
    
    # 度数が0の場合は空の分布を返す
    if hist.sum() == 0:
        return np.array([]), np.array([])

    # 度数分布を正規化して確率分布にする
    prob_dist = hist / hist.sum()
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    return prob_dist, bin_centers

def compute_kl_similarity(vec_a, vec_b, num_bins=10):
    """
    2つの連続値ベクトル間のKLダイバージェンスベースの類似度を計算する。
    """
    prob_a, _ = to_probability_distribution(vec_a, bins=num_bins)
    prob_b, _ = to_probability_distribution(vec_b, bins=num_bins)

    if prob_a.size == 0 or prob_b.size == 0:
        return 0.0

    kl_div_ab = compute_kl_divergence(prob_a, prob_b)
    kl_div_ba = compute_kl_divergence(prob_b, prob_a)
    
    avg_kl_div = (kl_div_ab + kl_div_ba) / 2.0
    return 1.0 / (1.0 + avg_kl_div)

def compute_wasserstein_similarity(vec_a, vec_b, num_bins=10):
    """
    2つの連続値ベクトル間のWasserstein距離ベースの類似度を計算する。
    """
    # 共通のビンエッジを決定
    all_data = np.concatenate((vec_a, vec_b))
    if all_data.size == 0:
        return 1.0 # 2つの空のベクトルは完全に類似している
        
    min_val, max_val = all_data.min(), all_data.max()
    # データが単一の値を持つ場合、有効なビン範囲を作成
    if min_val == max_val:
        min_val = min_val - 0.5
        max_val = max_val + 0.5
        
    common_bin_edges = np.linspace(min_val, max_val, num_bins + 1)

    # 共通のビンエッジで確率分布を計算
    prob_a, bin_centers_a = to_probability_distribution(vec_a, bins=common_bin_edges)
    prob_b, bin_centers_b = to_probability_distribution(vec_b, bins=common_bin_edges)

    # どちらかの分布が空の場合
    if prob_a.size == 0 and prob_b.size == 0:
        return 1.0 # 両方空なら類似
    if prob_a.size == 0 or prob_b.size == 0:
        return 0.0 # 片方だけ空なら非類似

    # Wasserstein距離を計算
    dist = compute_wasserstein_distance(bin_centers_a, bin_centers_b, u_weights=prob_a, v_weights=prob_b)
    
    # 距離を類似度に変換
    return 1.0 / (1.0 + dist)

def compute_self_correlation_score(vector):
    """
    ベクトルの前半と後半のピアソン相関係数を計算する。
    これにより、ベクトルの内部的な構造的連続性・安定性を評価する。
    """
    vec = np.asarray(vector, dtype=float)
    n = len(vec)
    if n < 2:
        return 0.0  # 2要素未満のベクトルでは相関は計算できない

    # ベクトルを前半と後半に分割
    mid = n // 2
    v1 = vec[:mid]
    v2 = vec[n-mid:] # 後半を末尾から取得することで、奇数長の場合に中央要素を自然に無視

    # 平均を計算
    mean1, mean2 = np.mean(v1), np.mean(v2)

    # 標準偏差を計算
    std1, std2 = np.std(v1), np.std(v2)

    # 標準偏差がゼロの場合、相関は計算できない（またはゼロとする）
    if std1 == 0 or std2 == 0:
        return 0.0

    # 共分散を計算
    covariance = np.mean((v1 - mean1) * (v2 - mean2))

    # ピアソン相関係数を計算
    correlation = covariance / (std1 * std2)
    
    return round(float(correlation), 4)