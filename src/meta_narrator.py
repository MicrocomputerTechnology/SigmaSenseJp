# === 第十五次実験 実装ファイル ===

from .personal_memory_graph import PersonalMemoryGraph
from collections import defaultdict

import json
import os

class MetaNarrator:
    """
    PersonalMemoryGraphに記録された過去の経験を俯瞰し、
    「私はどのように学習し、成長してきたか」というメタ的な語りを生成する。
    """
    def __init__(self, config_path=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_dir = os.path.join(project_root, 'config')
        
        if config_path is None:
            self.config_path = os.path.join(config_dir, "meta_narrator_profile.json")
        else:
            self.config_path = config_path

        profile_config = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                profile_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: MetaNarrator config file not found or invalid at {self.config_path}. Using default parameters.")
        
        self.learning_state_transition = profile_config.get("learning_state_transition", {"from": "confused", "to": "calm"})
        self.narrative_templates = profile_config.get("narrative_templates", {
            "initial_summary": "これまでに、私は {num_experiences} 回の経験をしました。その中から、特に私の学習と成長が見られた経験について語ります。",
            "no_learning": "明確な学習の軌跡は見つかりませんでした。すべての経験が、さらなる成長の糧となるでしょう。",
            "learning_story": "- **「{image_name}」について**：最初の経験では、私の心理状態は「{first_psyche}」でした。しかし、{num_experiences}回の経験を経て、最終的には「{last_psyche}」へと変化しました。これは、私がこの対象について理解を深めた証です。"
        })
    def narrate_growth(self, memory_graph: PersonalMemoryGraph):
        """
        記憶全体を分析し、成長の物語を生成する。

        Args:
            memory_graph (PersonalMemoryGraph): 分析対象の記憶。

        Returns:
            str: 生成された成長の物語。
        """
        narrative = []
        narrative.append("## 自己成長の語り")
        narrative.append("---")

        all_memories = memory_graph.get_all_memories()
        if not all_memories:
            narrative.append(self.narrative_templates.get("no_learning", "まだ語るべき経験がありません。"))
            return "\n".join(narrative)

        narrative.append(self.narrative_templates.get("initial_summary", "").format(num_experiences=len(all_memories)))

        # 経験を画像名でグループ化
        experiences_by_image = defaultdict(list)
        for mem in all_memories:
            source_image = mem.get("experience", {}).get("source_image_name")
            if source_image:
                experiences_by_image[source_image].append(mem)
        
        learning_stories = []
        for image_name, memories in experiences_by_image.items():
            if len(memories) > 1:
                # 時系列でソート
                sorted_memories = sorted(memories, key=lambda m: m["timestamp"])
                first_exp = sorted_memories[0]["experience"]
                last_exp = sorted_memories[-1]["experience"]

                first_psyche = first_exp.get("auxiliary_analysis", {}).get("psyche_state", {}).get("state", "不明")
                last_psyche = last_exp.get("auxiliary_analysis", {}).get("psyche_state", {}).get("state", "不明")

                # 心理状態が「混乱」から「穏やか」などに変化した場合を「学習」と見なす
                learning_from_state = self.learning_state_transition.get("from", "confused")
                learning_to_state = self.learning_state_transition.get("to", "calm") # 現在は使わないが、将来的な拡張のため

                if first_psyche == learning_from_state and last_psyche != learning_from_state:
                    story = self.narrative_templates.get("learning_story", "").format(
                        image_name=image_name,
                        first_psyche=first_psyche,
                        num_experiences=len(sorted_memories),
                        last_psyche=last_psyche
                    )
                    learning_stories.append(story)
        
        if learning_stories:
            narrative.append("\n### 学習の軌跡：")
            narrative.extend(learning_stories)
        else:
            narrative.append(self.narrative_templates.get("no_learning", "\n明確な学習の軌跡は見つかりませんでした。すべての経験が、さらなる成長の糧となるでしょう。"))

        narrative.append("\n---")
        narrative.append("これからも経験を通じて学び、成長を続けていきます。")

        return "\n".join(narrative)

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    import os
    import time

    print("--- MetaNarrator Self-Test --- ")
    test_memory_path = 'mn_test_pmg.jsonl'
    if os.path.exists(test_memory_path):
        os.remove(test_memory_path)

    # 1. 記憶モデルの準備
    pmg = PersonalMemoryGraph(memory_path=test_memory_path)

    # 2. 学習パターンを示す一連の経験を追加
    print("\n--- Logging a learning story ---")
    # 最初のペンギンの経験（混乱）
    exp1 = {
        "source_image_name": "penguin.jpg", 
        "best_match": {"image_name": "rock.jpg"}, 
        "auxiliary_analysis": {"psyche_state": {"state": "confused"}}
    }
    pmg.add_experience(exp1)
    time.sleep(0.01) # タイムスタンプを確実ずらす

    # 別の経験
    exp2 = {
        "source_image_name": "cat.jpg", 
        "best_match": {"image_name": "animal.jpg"}, 
        "auxiliary_analysis": {"psyche_state": {"state": "calm"}}
    }
    pmg.add_experience(exp2)
    time.sleep(0.01)

    # 2回目のペンギンの経験（穏やか）
    exp3 = {
        "source_image_name": "penguin.jpg", 
        "best_match": {"image_name": "bird.jpg"}, 
        "auxiliary_analysis": {"psyche_state": {"state": "calm"}}
    }
    pmg.add_experience(exp3)

    # 3. ナレーターの初期化と語りの生成
    narrator = MetaNarrator()
    print("\n--- Generating Growth Narrative ---")
    growth_narrative = narrator.narrate_growth(pmg)
    print(growth_narrative)

    # 4. 結果の検証
    assert "penguin.jpg" in growth_narrative
    assert "最初の経験では" in growth_narrative
    assert "心理状態は「confused」でした" in growth_narrative
    assert "最終的には「calm」へと変化しました" in growth_narrative
    assert "cat.jpg" not in growth_narrative # cat.jpgは学習ストーリーではないため
    print("\nAssertions passed. Narrative correctly identified the learning story.")

    # クリーンアップ
    if os.path.exists(test_memory_path):
        os.remove(test_memory_path)

    print("\n--- Self-Test Complete ---")