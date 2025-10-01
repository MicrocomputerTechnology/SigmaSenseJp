import json
import os

class ConfigLoader:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.configs = self._load_all_configs()

    def _load_all_configs(self):
        loaded_configs = {}
        if not os.path.exists(self.config_dir):
            print(f"Warning: Config directory not found at {self.config_dir}")
            return loaded_configs

        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config_name = os.path.splitext(filename)[0]
                        loaded_configs[config_name] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {filepath}. Skipping.")
                except Exception as e:
                    print(f"Warning: Error loading config from {filepath}: {e}. Skipping.")
        return loaded_configs

    def get_config(self, config_name):
        return self.configs.get(config_name)

    def get_all_configs(self):
        return self.configs
