
import json
import random
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

    def __init__(self, output_path=None):
        if output_path is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            log_dir = os.path.join(project_root, "sigma_logs")
            self.output_path = os.path.join(log_dir, "psyche_log.jsonl")
        else:
            self.output_path = output_path
        self.agents = [
            "selia", "nova", "lyra", "saphiel",
            "orien", "vetra", "aegis"
        ]
        # Base emotional states (tendencies)
        self.base_emotions = {
            "selia": 0.7,   # Orderly, so stable
            "nova": 0.4,    # Deviant, so more volatile
            "lyra": 0.5,    # Emotional, so average base but wide swings
            "saphiel": 0.8, # Generative, positive
            "orien": 0.9,   # Integrative, stable
            "vetra": 0.6,   # Memory/Ethics, thoughtful
            "aegis": 0.7    # Boundary, stable but firm
        }

    def generate_log(self, time_steps=10):
        """
        Generates a simulated log for a number of time steps.
        """
        print_header(f"Generating Simulated Psyche Log for {time_steps} time steps")
        
        # Simulate a conversation that starts coherent, becomes chaotic, then resolves.
        coherence_trend = [0.8, 0.9, 0.7, 0.5, 0.3, 0.4, 0.6, 0.8, 0.9, 0.9]
        divergence_trend = [0.1, 0.1, 0.2, 0.4, 0.7, 0.6, 0.3, 0.2, 0.1, 0.1]

        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for t in range(time_steps):
                log_entry = {"t": t}
                emotions = {}
                for agent in self.agents:
                    base = self.base_emotions[agent]
                    fluctuation = random.uniform(-0.2, 0.2)
                    if agent in ["nova", "lyra"]: fluctuation *= 2
                    emotions[f"E_{agent}"] = round(max(0, min(1, base + fluctuation)), 4)
                log_entry.update(emotions)

                log_entry["I"] = round(max(0, min(1, coherence_trend[t] + random.uniform(-0.05, 0.05))), 4)
                log_entry["R"] = round(max(0, min(1, divergence_trend[t] + random.uniform(-0.05, 0.05))), 4)

                f.write(json.dumps(log_entry) + '\n')
        
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
