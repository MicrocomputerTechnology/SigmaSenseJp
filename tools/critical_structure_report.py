# 全理論：照合不能群の意味軸分布を記述し、意味空間の再設計に必要な構造的知見を抽出する

import sys
import os

# 親ディレクトリをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.critical_structure_mapper import map_critical_structure

def generate_critical_report():
    criticals = map_critical_structure()
    print("\n🚨 臨界構造レポート（照合不能群）")
    print("-" * 40)
    for c in criticals:
        print(f"画像: {c['image']}")
        print(f"  エントロピー: {c['entropy']}, スパース度: {c['sparsity']}")
        print(f"  色集中度: {c['color_concentration']}, 空間距離: {c['spatial_distance']}")
        print(f"  包含率: {c['inclusion_rate']}, 文脈距離: {c['context_score']}")
        print(f"  群サイズ: {c['group_size']}, 明るさ: {c['brightness']}, 陰影強度: {c['shadow_strength']}")
        print("-" * 40)
    print("このレポートは、意味空間の折れ目（照合不能が集中する構造）を記述するための基盤です。")

if __name__ == "__main__":
    generate_critical_report()
