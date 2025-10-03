class TimeConstrainedReasoner:
    def __init__(self, symbolic_reasoner, planner):
        pass

    def reason_with_time_limit(self, context: dict, time_limit_ms: int) -> dict:
        pass

    def plan_with_time_limit(self, goal: dict, current_state: dict, time_limit_ms: int) -> list[dict]:
        pass
