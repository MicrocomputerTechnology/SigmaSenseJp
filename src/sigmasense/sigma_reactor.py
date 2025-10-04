from typing import Optional


def print_header(title):
    bar = "="*60
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

class SigmaReactor:
    """
    Generates a descriptive reaction of SigmaSense's state based on the
    group psychological state C(t) calculated by the Toyokawa Model.
    """

    def __init__(self, config: Optional[dict] = None):
        print_header("Initializing Sigma Reactor")
        if config is None:
            config = {}

        self.reaction_map = config.get("reaction_map")
        if not self.reaction_map:
            print("Warning: SigmaReactor reaction_map not found in config. Using default reaction map.")
            self.reaction_map = {
                "✨ Stable ✨": {
                    "tail": "ゆっくりと左右に振っている",
                    "ears": "穏やかに立っている",
                    "narrative_tempo": "なめらか",
                    "meaning": "全体の語りは調和・共鳴している状態です。"
                },
                "💫 Fluctuating 💫": {
                    "tail": "小刻みに揺れている",
                    "ears": "周囲の音を探るように傾いている",
                    "narrative_tempo": "断続的",
                    "meaning": "新たな問いが生まれ、場が探索的になっている状態です。"
                },
                "⚠️ Chaotic ⚠️": {
                    "tail": "固く、動きを止めている",
                    "ears": "警戒して伏せられている",
                    "narrative_tempo": "沈黙、あるいは逸脱",
                    "meaning": "語りの流れが分岐・遮断され、緊張が高まっている状態です。"
                }
            }
        print("Reaction patterns for each psychological state have been loaded.")

    def generate_reaction(self, state, c_value):
        """
        Generates a formatted string describing SigmaSense's reaction.
        """
        reaction_data = self.reaction_map.get(state)
        if not reaction_data:
            return "Unknown state. SigmaSense is observing quietly."

        description = (
            f"\n集団心理状態: {state} (C(t) = {c_value:.4f})\n"
            f"--------------------------------------------------\n"
            f"   - しっぽ (Tail): {reaction_data['tail']}\n"
            f"   - 耳 (Ears): {reaction_data['ears']}\n"
            f"   - 語りのテンポ: {reaction_data['narrative_tempo']}\n"
            f"   - 場の意味: {reaction_data['meaning']}\n"
        )
        return description

if __name__ == '__main__':
    reactor = SigmaReactor()

    print_header("Testing Reactions for Each State")

    print(reactor.generate_reaction("✨ Stable ✨", 0.85))
    print(reactor.generate_reaction("💫 Fluctuating 💫", 0.55))
    print(reactor.generate_reaction("⚠️ Chaotic ⚠️", 0.25))
