from .information_metrics import compute_entropy, compute_kl_divergence

class ReconstructionTrigger:
    """
    再構成トリガーの発火条件を判定するクラス。
    """

    def __init__(self, config: dict = None):
        if config is None:
            config = {}
        
        self.threshold_entropy = config.get("threshold_entropy", 2.5)
        self.threshold_kl = config.get("threshold_kl", 1.0)

    def should_trigger_reconstruction(self, vector_p, vector_q=None):
        """
        再構成トリガーの発火条件を判定する。

        - ベクトルが1つの場合: 情報量（エントロピー）が閾値を下回った場合にTrueを返す。
        - ベクトルが2つの場合: 2つのベクトルのKLダイバージェンスが閾値を超えた場合にTrueを返す。
        """
        if vector_q is None:
            # エントロピーチェック
            entropy = compute_entropy(vector_p)
            return entropy < self.threshold_entropy
        else:
            # KLダイバージェンスチェック
            divergence = compute_kl_divergence(vector_p, vector_q)
            return divergence > self.threshold_kl