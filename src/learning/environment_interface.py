class Environment:
    def get_state(self) -> dict:
        pass

    def execute_action(self, action: dict) -> dict:
        pass

    def get_reward(self) -> float:
        pass

    def is_terminal(self) -> bool:
        pass
