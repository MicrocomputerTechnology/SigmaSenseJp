
import json
import os

class PsycheModulator:
    """
    Observes the system's internal state (psyche) based on activity logs
    and provides modulations for other auxiliary units.
    This is a simplified interpretation of the 'Toyokawa Model'.
    """
    def __init__(self, log_path="psyche_log.jsonl"):
        """
        Initializes the modulator.
        """
        print("Initializing Psyche Modulator...")
        self.log_path = log_path

    def get_current_state(self):
        """
        Calculates the current psychological state based on activity logs.

        Returns:
            dict: A dictionary representing the current system state.
        """
        if not os.path.exists(self.log_path):
            return {"state": "Calm", "activity_level": 0, "reason": "No log file found."}

        try:
            with open(self.log_path, 'r') as f:
                # Count log entries as a simple proxy for activity level.
                activity_level = sum(1 for line in f)
            
            if activity_level > 100:
                state = "Agitated"
                reason = f"High volume of internal activity ({activity_level} events)."
            elif activity_level > 20:
                state = "Active"
                reason = f"Moderate level of internal activity ({activity_level} events)."
            else:
                state = "Calm"
                reason = f"Low level of internal activity ({activity_level} events)."

            return {"state": state, "activity_level": activity_level, "reason": reason}

        except Exception as e:
            return {"state": "Unknown", "activity_level": -1, "reason": f"Error reading psyche log: {e}"}

    def modulate_prediction(self, prediction, psyche_state):
        """
        Modulates the output of the MatchPredictor based on the psyche state.
        For example, an 'Agitated' state might lower confidence.
        (This is a placeholder for future, more complex integration).
        """
        if psyche_state.get("state") == "Agitated":
            prediction['score'] *= 0.9 # Reduce confidence slightly
            prediction['reason'] += " (Modulated by Agitated state)"
        return prediction

if __name__ == '__main__':
    # Create a dummy log file for testing
    dummy_log_path = "psyche_log.jsonl"
    # Simulate an 'Active' state
    with open(dummy_log_path, 'w') as f:
        for i in range(30):
            f.write(f'{{"event": "test_event_{i}"}}\n')

    print("--- Running PsycheModulator Tests ---")
    modulator = PsycheModulator(log_path=dummy_log_path)
    state = modulator.get_current_state()
    print(f"\nCurrent Psyche State: {state}")

    # Test modulation
    print("\n--- Testing Modulation ---")
    initial_prediction = {"score": 0.8, "reason": "Initial reason."}
    agitated_state = {"state": "Agitated"}
    modulated_prediction = modulator.modulate_prediction(initial_prediction, agitated_state)
    print(f"Modulated Prediction (Agitated): {modulated_prediction}")
    
    os.remove(dummy_log_path)
