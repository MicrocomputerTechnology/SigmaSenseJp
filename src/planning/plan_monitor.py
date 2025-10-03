class PlanMonitor:
    def __init__(self, world_model, planner, action_executor):
        pass

    def monitor_plan(self, plan: list[dict]) -> dict:
        pass

    def detect_deviation(self, plan: list[dict], current_state: dict) -> bool:
        pass

    def request_replanning(self, current_state: dict, failed_step: dict) -> list[dict]:
        pass
