import numpy as np

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
