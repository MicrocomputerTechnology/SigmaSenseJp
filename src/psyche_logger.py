
import json
import random
import os

import json
import os

def print_header(title):
    bar = "="*60
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

class PsycheLogger:
    """
    Simulates and logs the emotional states (E), coherence (I), and
    divergence (R) of the Octa agents over time.
    This serves as the input data generator for the Toyokawa Model.
    """

    def __init__(self, output_path=None, config_path=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        log_dir = os.path.join(project_root, "sigma_logs")
        
        if output_path is None:
            self.output_path = os.path.join(log_dir, "psyche_log.jsonl")
        else:
            self.output_path = output_path

        config_dir = os.path.join(project_root, 'config')
        if config_path is None:
            self.config_path = os.path.join(config_dir, "psyche_logger_profile.json")
        else:
            self.config_path = config_path

        profile_config = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                profile_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: PsycheLogger config file not found or invalid at {self.config_path}. Using default parameters.")

        self.agents = profile_config.get("agents", [
            "selia", "nova", "lyra", "saphiel",
            "orien", "vetra", "aegis"
        ])
        self.base_emotions = profile_config.get("base_emotions", {
            "selia": 0.7,   # Orderly, so stable
            "nova": 0.4,    # Deviant, so more volatile
            "lyra": 0.5,    # Emotional, so average base but wide swings
            "saphiel": 0.8, # Generative, positive
            "orien": 0.9,   # Integrative, stable
            "vetra": 0.6,   # Memory/Ethics, thoughtful
            "aegis": 0.7    # Boundary, stable but firm
        })
        self.time_steps = profile_config.get("time_steps", 10)
        self.coherence_trend = profile_config.get("coherence_trend", [0.8, 0.9, 0.7, 0.5, 0.3, 0.4, 0.6, 0.8, 0.9, 0.9])
        self.divergence_trend = profile_config.get("divergence_trend", [0.1, 0.1, 0.2, 0.4, 0.7, 0.6, 0.3, 0.2, 0.1, 0.1])
        self.fluctuation_range = profile_config.get("fluctuation_range", {"min": -0.2, "max": 0.2})
        self.fluctuation_multiplier_volatile_agents = profile_config.get("fluctuation_multiplier_volatile_agents", 2)
    def generate_log(self):
        """
        Generates a simulated log for a number of time steps.
        """
        print_header(f"Generating Simulated Psyche Log for {self.time_steps} time steps")
        
        # Simulate a conversation that starts coherent, becomes chaotic, then resolves.
        # Parameters are now loaded from config

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for t in range(self.time_steps):
                log_entry = {"t": t}
                emotions = {}
                for agent in self.agents:
                    base = self.base_emotions[agent]
                    fluctuation = random.uniform(self.fluctuation_range["min"], self.fluctuation_range["max"])
                    if agent in ["nova", "lyra"]: fluctuation *= self.fluctuation_multiplier_volatile_agents
                    emotions[f"E_{agent}"] = round(max(0, min(1, base + fluctuation)), 4)
                log_entry.update(emotions)

                # coherence_trendとdivergence_trendはconfigからロードされたものを使用
                coherence_val = self.coherence_trend[t] if t < len(self.coherence_trend) else self.coherence_trend[-1]
                divergence_val = self.divergence_trend[t] if t < len(self.divergence_trend) else self.divergence_trend[-1]

                log_entry["I"] = round(max(0, min(1, coherence_val + random.uniform(-0.05, 0.05))), 4)
                log_entry["R"] = round(max(0, min(1, divergence_val + random.uniform(-0.05, 0.05))), 4)

                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        print(f"Successfully generated and saved log to '{self.output_path}'")

if __name__ == '__main__':
    logger = PsycheLogger()
    logger.generate_log()

    print_header("Verifying Generated Log File")
    try:
        with open(logger.output_path, 'r') as f:
            for i, line in enumerate(f):
                if i < 3:
                    print(f"t={i}: {line.strip()}")
                else:
                    break
    except FileNotFoundError:
        print(f"Log file {logger.output_path} not found for verification.")
