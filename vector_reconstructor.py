# 構造抽出理論：意味ベクトルの欠損構造を補完し、再構成力を回復する
# 情報理論：スパース度の高いベクトルに対して平均値補完を行う
import numpy as np

def reconstruct_vector(original_vec):
    """
    ゼロ成分を平均値で補完し、正規化された再構成ベクトルを返す。
    """
    vec = np.array(original_vec, dtype=np.float32)
    mean_val = np.mean(vec[vec != 0]) if np.any(vec != 0) else 0.1
    reconstructed = np.where(vec == 0, mean_val, vec)
    norm = np.linalg.norm(reconstructed)
    return np.round(reconstructed / norm, 4).tolist() if norm != 0 else reconstructed.tolist()
