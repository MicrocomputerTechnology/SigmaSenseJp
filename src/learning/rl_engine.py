class RLEngine:
    def __init__(self, environment, reactor, reward_function, growth_tracker):
        pass

    def learn(self, num_episodes: int):
        pass

    def choose_action(self, state: dict) -> dict:
        pass

    def update_policy(self, state, action, reward, next_state):
        pass
