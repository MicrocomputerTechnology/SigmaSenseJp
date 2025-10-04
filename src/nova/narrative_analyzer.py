import json
import numpy as np

class NarrativeAnalyzer:
    """
    個人的な経験のログ（personal_memory.jsonl）を分析し、
    特定の主題に関する物語や意味の系譜を再構成する。
    """

    def __init__(self, log_file_path):
        """
        Args:
            log_file_path (str): 分析対象の.jsonlログファイルのパス。
        """
        self.log_file_path = log_file_path
        self.experiences = self._load_experiences()

    def _load_experiences(self):
        """ログファイルからすべての経験を読み込み、時系列順にソートする。"""
        experiences = []
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        # 'experience' キーが存在し、その中に 'timestamp' があるか確認
                        if 'experience' in data and 'timestamp' in data['experience']:
                             # timestampをdatetimeオブジェクトに変換してソートキーとして使用
                            experiences.append(data['experience'])
                        elif 'timestamp' in data: # 旧フォーマットへの後方互換性
                            experiences.append(data)

                    except json.JSONDecodeError:
                        # JSONデコードエラーは無視
                        continue
            
            # タイムスタンプでソート
            experiences.sort(key=lambda x: x.get('timestamp', ''))
            return experiences
        except FileNotFoundError:
            print(f"❗エラー: ログファイルが見つかりません: {self.log_file_path}")
            return []

    def trace_narrative_for_image(self, image_name):
        """
        特定の画像名に関するすべての経験を時系列で追跡し、物語を生成する。

        Args:
            image_name (str): 追跡する画像のファイル名 (例: 'circle_center.jpg')

        Returns:
            list: 追跡された経験のリスト。
        """
        print(f"--- 📖 物語の追跡を開始: '{image_name}' ---")
        
        related_experiences = [
            exp for exp in self.experiences 
            if exp.get('source_image_name') == image_name
        ]

        if not related_experiences:
            print("  -> 関連する経験は見つかりませんでした。")
            return []

        print(f"  -> {len(related_experiences)}件の関連する経験を発見しました。")
        
        for i, exp in enumerate(related_experiences):
            timestamp = exp.get('timestamp', 'N/A')
            best_match = exp.get('best_match', {})
            match_name = best_match.get('image_name', 'N/A')
            score = best_match.get('score', 0.0)
            
            print(f"\n  [経験 {i+1}]")
            print(f"    - タイムスタンプ: {timestamp}")
            print(f"    - 最良一致: '{match_name}' (スコア: {score:.4f})")

            # 'Unrelated' の場合の診断
            if match_name is None or 'unrelated' in str(match_name).lower():
                diagnoses = self._diagnose_unrelated_vector(exp.get('vector', []))
                if diagnoses:
                    print("    - 診断 (情報不足の可能性):")
                    for d in diagnoses:
                        print(f"      - {d}")

        return related_experiences

    def _diagnose_unrelated_vector(self, vector):
        """
        単一のベクトルを分析し、情報不足の可能性のある軸を特定する。
        (nova_diagnoser.pyのロジックを簡略化して統合)
        """
        if not isinstance(vector, list) or not vector:
            return []
        
        # 簡単な診断: ベクトルの要素のほとんどが0に近い場合、情報不足と判断
        non_zero_elements = np.count_nonzero(np.array(vector) > 0.1)
        total_elements = len(vector)
        
        if total_elements > 0 and (non_zero_elements / total_elements) < 0.1: # 10%未満しか有効な特徴がない場合
            return [f"特徴の大部分が低活性です (有効特徴: {non_zero_elements}/{total_elements})"]
            
        return []
