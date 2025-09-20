from .information_metrics import compute_entropy, kl_divergence

def should_trigger_reconstruction(vector_p, vector_q=None, threshold_entropy=2.5, threshold_kl=1.0):
    """
    再構成トリガーの発火条件を判定する。

    - ベクトルが1つの場合: 情報量（エントロピー）が閾値を下回った場合にTrueを返す。
    - ベクトルが2つの場合: 2つのベクトルのKLダイバージェンスが閾値を超えた場合にTrueを返す。
    """
    if vector_q is None:
        # エントロピーチェック
        entropy = compute_entropy(vector_p)
        return entropy < threshold_entropy
    else:
        # KLダイバージェンスチェック
        divergence = kl_divergence(vector_p, vector_q)
        return divergence > threshold_kl