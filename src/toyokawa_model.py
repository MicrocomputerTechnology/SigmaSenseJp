
import json
import os

def print_header(title):
    bar = "="*60
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

class ToyokawaModel:
    """
    Implements the Toyokawa Model to calculate the group psychological state C(t)
    from the psyche log.
    C(t) = Σₗ αₗ × Eₗ(t) + β × I(t) + γ × R(t)
    """

    def __init__(self, config: dict = None, log_path: str = None):
        print_header("Initializing Toyokawa Model")
        if config is None:
            config = {}

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        log_dir = os.path.join(project_root, 'sigma_logs')
        self.log_path = log_path or os.path.join(log_dir, "psyche_log.jsonl")

        self.agents = config.get("agents", ["selia", "nova", "lyra", "saphiel", "orien", "vetra", "aegis"])
        
        # Load model weights from config
        self.weights = config.get("weights")
        if not self.weights:
            print("Warning: ToyokawaModel weights not found in config. Using default weights.")
            self.weights = {
                "alpha": {f"E_{agent}": 1.0/len(self.agents) for agent in self.agents},
                "beta": 0.5,  # Weight for coherence (positive impact)
                "gamma": -0.5, # Weight for divergence (negative impact)
            }

        print("Model weights (α, β, γ) have been set.")
        print(f'  - Alpha (αᵢ): {self.weights.get("alpha", {}).get(f"E_{self.agents[0]}", 0):.2f} for each agent')
        print(f'  - Beta (β): {self.weights.get("beta", 0)}')
        print(f"  - Gamma (γ): {self.weights.get("gamma", 0)}")

    def load_log(self):
        """Loads the psyche log file."""
        if not os.path.exists(self.log_path):
            raise FileNotFoundError(f"Psyche log file not found at '{self.log_path}'")
        log_data = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                log_data.append(json.loads(line))
        return log_data

    def calculate_c_t(self, log_entry):
        """Calculates C(t) for a single time step."""
        sum_of_emotions = 0
        for agent in self.agents:
            sum_of_emotions += self.weights["alpha"][f"E_{agent}"] * log_entry.get(f"E_{agent}", 0)
            
        coherence_term = self.weights["beta"] * log_entry.get("I", 0)
        divergence_term = self.weights["gamma"] * log_entry.get("R", 0)
        
        return sum_of_emotions + coherence_term + divergence_term

    def interpret_state(self, c_value):
        """Interprets the C(t) value into a qualitative state."""
        if c_value > 0.75:
            return "✨ Stable ✨"
        elif c_value > 0.4:
            return "💫 Fluctuating 💫"
        else:
            return "⚠️ Chaotic ⚠️"

    def run_analysis(self):
        """Runs the full analysis on the log file."""
        print_header(f"Running Toyokawa Model Analysis on '{self.log_path}'")
        try:
            log_data = self.load_log()
            results = []
            for entry in log_data:
                t = entry.get("t")
                c_value = self.calculate_c_t(entry)
                state = self.interpret_state(c_value)
                results.append({"t": t, "C(t)": c_value, "state": state})
                print(f"Time t={t:02d}: C(t) = {c_value:.4f} -> State: {state}")
            return results
        except FileNotFoundError as e:
            print(e)
            return None

if __name__ == '__main__':
    model = ToyokawaModel()
    analysis_results = model.run_analysis()
    if analysis_results:
        print("\nAnalysis complete.")
