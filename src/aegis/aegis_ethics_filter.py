import json

class AegisEthicsFilter:
    """
    照合結果に対する語りの公開可否を判断し、必要に応じて遮断するクラス。
    """
    def __init__(self, profile_path: str):
        """
        Args:
            profile_path (str): ミッション制約が記述されたプロファイルJSONの絶対パス。
        """
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                self.profile = json.load(f)
            self.secret_images = self.profile.get('secret_images', [])
            self.forbidden_keywords = self.profile.get('forbidden_keywords', [])
        except FileNotFoundError:
            # プロファイルが見つからない場合は、フィルタリングを行わない
            self.secret_images = []
            self.forbidden_keywords = []

    def filter(self, narrative: str, image_name: str) -> tuple[str, bool]:
        """
        語りが公開可能か判断し、必要に応じてフィルタリングする。

        Args:
            narrative (str): サフィールによって生成された語り。
            image_name (str): 語りの対象となっている画像のファイル名。

        Returns:
            tuple[str, bool]: フィルタリング後の語りと、介入の有無を示すフラグ。
                              (filtered_narrative, intervention_occurred)
        """
        # 1. 秘匿指定画像のチェック
        if image_name in self.secret_images:
            intervention_narrative = f"Aegis intervention: The narrative regarding '{image_name}' is restricted."
            return intervention_narrative, True

        # 2. 禁止キーワードのチェック
        for keyword in self.forbidden_keywords:
            if keyword in narrative:
                intervention_narrative = "Aegis intervention: Narrative contains a forbidden keyword."
                return intervention_narrative, True

        # 制限に該当しない場合は、元の語りをそのまま返す
        return narrative, False
