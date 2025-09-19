# 情報理論：エントロピーとスパース度に基づき、意味的断絶を検出する
def should_trigger_reconstruction(entropy, sparsity, threshold_entropy=2.5, threshold_sparsity=0.4):
    """
    再構成トリガーの発火条件を判定する。
    情報密度が低い、またはスパース度が高い場合にTrueを返す。
    """
    return entropy < threshold_entropy or sparsity > threshold_sparsity
