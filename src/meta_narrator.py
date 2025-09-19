# === 第十五次実験 実装ファイル ===

from .personal_memory_graph import PersonalMemoryGraph
from collections import defaultdict

class MetaNarrator:
    """
    PersonalMemoryGraphに記録された過去の経験を俯瞰し、
    「私はどのように学習し、成長してきたか」というメタ的な語りを生成する。
    """

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
            narrative.append("まだ語るべき経験がありません。")
            return "\n".join(narrative)

        narrative.append(f"これまでに、私は {len(all_memories)} 回の経験をしました。その中から、特に私の学習と成長が見られた経験について語ります。")

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
                if first_psyche == "confused" and last_psyche != "confused":
                    story = f"- **「{image_name}」について**：最初の経験では、私の心理状態は「{first_psyche}」でした。しかし、{len(sorted_memories)}回の経験を経て、最終的には「{last_psyche}」へと変化しました。これは、私がこの対象について理解を深めた証です。"
                    learning_stories.append(story)
        
        if learning_stories:
            narrative.append("\n### 学習の軌跡：")
            narrative.extend(learning_stories)
        else:
            narrative.append("\n明確な学習の軌跡は見つかりませんでした。すべての経験が、さらなる成長の糧となるでしょう。")

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