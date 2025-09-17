import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy.stats import entropy as scipy_entropy

def extract_color_clusters(img, n_clusters=5):
    """
    画像データから主要な色クラスタを検出し、その数と色のエントロピーを返す。
    """
    if img is None:
        return {"cluster_count": 0, "entropy": 0.0}

    # 画像をピクセルのリストに変換
    pixels = img.reshape(-1, 3)
    pixels = np.float32(pixels)

    # K-meansで色をクラスタリング
    # n_init='auto' に設定して将来の警告を抑制
    kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42).fit(pixels)
    
    # 各クラスタのピクセル数を計算
    labels = kmeans.labels_
    counts = np.bincount(labels)
    
    # 有意なクラスタの数をカウント（例：全ピクセルの1%以上を占めるクラスタ）
    min_pixels = len(pixels) * 0.01
    significant_clusters = np.sum(counts > min_pixels)

    # 色の分布からエントロピーを計算
    proportions = counts / len(pixels)
    color_entropy = scipy_entropy(proportions, base=2)

    return {
        "cluster_count": significant_clusters,
        "entropy": color_entropy
    }
