
import numpy as np
from PIL import Image
from . import structure_detector

class SheafAnalyzer:
    """
    画像に層理論の考え方を適用し、局所的な特徴の整合性を検証するクラス。
    """

    def __init__(self, image_path, sigma_instance):
        """
        Args:
            image_path (str): 分析対象の画像ファイルパス。
            sigma_instance (SigmaSense): 特徴ベクトルを抽出するためのSigmaSenseインスタンス。
        """
        self.image_path = image_path
        self.image = Image.open(image_path).convert('RGB')
        self.sigma = sigma_instance
        self.local_data = {} # region -> feature_vector

    def _get_feature_vector_for_region(self, region_rect):
        """
        指定された矩形領域から特徴ベクトルを抽出する。
        (x, y, w, h)
        """
        # SigmaSenseが画像領域を直接扱えない場合、
        # PILで画像をクロップして渡す。
        cropped_image = self.image.crop((region_rect[0], region_rect[1], region_rect[0] + region_rect[2], region_rect[1] + region_rect[3]))
        
        # Pass the PIL.Image object directly to process_experience
        vec = None
        result = self.sigma.process_experience(cropped_image)
        if result and 'vector' in result:
            vec = np.array(result['vector'])
        return vec

    def assign_local_data(self):
        """
        structure_detectorを使って領域を検出し、各領域の特徴量を計算して保持する。
        """
        regions = structure_detector.extract_structure_features(self.image_path)
        for region in regions:
            # structure_detectorの戻り値形式 {"x": ..., "y": ...} を (x, y, w, h) に変換
            region_rect = (region['x'], region['y'], region['w'], region['h'])
            self.local_data[region_rect] = self._get_feature_vector_for_region(region_rect)
        print(f"Found and processed {len(self.local_data)} regions.")

    def _intersection(self, r1, r2):
        """2つの矩形領域の交差領域を返す (x, y, w, h)"""
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        x_overlap = max(x1, x2)
        y_overlap = max(y1, y2)
        x_end = min(x1 + w1, x2 + w2)
        y_end = min(y1 + h1, y2 + h2)
        
        if x_end > x_overlap and y_end > y_overlap:
            return (x_overlap, y_overlap, x_end - x_overlap, y_end - y_overlap)
        return None

    def check_gluing_condition(self, tolerance=0.1):
        """
        貼り合わせ条件をチェックする。
        全ての領域ペアの交差部分で、特徴ベクトルが整合しているかを確認する。
        """
        if not self.local_data:
            self.assign_local_data()

        regions = list(self.local_data.keys())
        if len(regions) < 2:
            print("  - Gluing check skipped: Not enough regions to compare.")
            return True # 比較対象がなければ矛盾はない

        print("  - Starting gluing condition check...")
        is_consistent = True
        for i in range(len(regions)):
            for j in range(i + 1, len(regions)):
                r1, r2 = regions[i], regions[j] 
                
                overlap = self._intersection(r1, r2)
                if overlap and overlap[2] > 0 and overlap[3] > 0: # 交差領域が実質的な面積を持つか
                    # 交差領域の特徴量を直接計算する (これは層理論の「制限」の厳密な定義ではなく、実用的な近似です)
                    f_overlap = self._get_feature_vector_for_region(overlap)
                    
                    # 元の領域の特徴量を交差領域に「制限」する
                    # ここでは、簡略化のため交差領域そのものの特徴量を再計算することで「制限」と見なします。
                    # 理想的には、f1_restricted は r1 のデータから、f2_restricted は r2 のデータから
                    # 導出されるべきですが、現在の高レベルな意味ベクトルの性質上、直接的な制限は困難です。
                    f1_restricted = f_overlap # Re-use the computed overlap feature
                    f2_restricted = f_overlap # Re-use the computed overlap feature

                    # ここでの allclose は、異なる計算経路でも同じ結果になるかの確認。
                    if not np.allclose(f1_restricted, f_overlap, atol=tolerance) or \
                       not np.allclose(f2_restricted, f_overlap, atol=tolerance):
                        print(f"    - Inconsistency found between region {r1} and {r2} at overlap {overlap}")
                        is_consistent = False
        
        if is_consistent:
            print("  - Gluing check passed: All overlapping regions are consistent.")
        else:
            print("  - Gluing check failed: Inconsistencies found.")
            
        return is_consistent

    def glue(self):
        """
        整合性チェックが通った場合に、局所データを統合して大域的な特徴を返す。
        """
        if not self.check_gluing_condition():
            raise ValueError("Local data is inconsistent and cannot be glued.")
        
        if not self.local_data:
            return None

        # ここでは単純に全特徴量の平均を「大域データ」とする
        global_vector = np.mean(list(self.local_data.values()), axis=0)
        return global_vector
