import json
import os
from .information_metrics import compute_entropy, compute_kl_divergence

class ReconstructionTrigger:
    """
    再構成トリガーの発火条件を判定するクラス。
    """

    def __init__(self, config_path=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_dir = os.path.join(project_root, 'config')
        
        if config_path is None:
            self.config_path = os.path.join(config_dir, "reconstruction_trigger_profile.json")
        else:
            self.config_path = config_path

        profile_config = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                profile_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: ReconstructionTrigger config file not found or invalid at {self.config_path}. Using default parameters.")
        
        self.threshold_entropy = profile_config.get("threshold_entropy", 2.5)
        self.threshold_kl = profile_config.get("threshold_kl", 1.0)

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