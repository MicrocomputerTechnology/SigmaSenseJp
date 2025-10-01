# 全理論：照合不能群の意味軸分布を記述し、意味空間の再設計に必要な構造的知見を抽出する

import sys
import os

# 親ディレクトリ（プロジェクトルート）をパスに追加
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# srcディレクトリをパスに追加
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.sigmasense.critical_structure_mapper import map_critical_structure
from src.sigmasense.config_loader import ConfigLoader

def generate_critical_report():
    config_loader = ConfigLoader(os.path.join(project_root, 'config'))
    cs_config = config_loader.get_config('critical_structure_mapper_profile')
    if not cs_config:
        print("Warning: critical_structure_mapper_profile.json not found. Using default threshold.")
        cs_config = {}

    criticals = map_critical_structure(cs_config)
    
    print("\n🚨 臨界構造レポート（照合不能群）")
    print("-" * 40)
    # Check if the function returned a report or a message
    if criticals.get("unmatchable_count", 0) > 0:
        # Assuming the function returns a dictionary with a specific structure
        # This part might need adjustment based on the actual return value
        print(f"照合不能群の数: {criticals.get('unmatchable_count')}")
        print("臨界ベクトル（名前付き）:")
        for dim, value in criticals.get("critical_structure_named", {}).items():
            print(f"  {dim}: {value:.4f}")
    else:
        print(criticals.get("message", "臨界構造は見つかりませんでした。"))
    print("-" * 40)
    print("このレポートは、意味空間の折れ目（照合不能が集中する構造）を記述するための基盤です。")

if __name__ == "__main__":
    generate_critical_report()
