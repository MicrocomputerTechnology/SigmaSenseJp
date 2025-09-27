## Warning: ToyokawaModel Weights Not Found in `run_psyche_simulation.py`

When running `scripts/run_psyche_simulation.py`, a warning was issued regarding missing `ToyokawaModel` weights.

### Warning Message

```
Warning: ToyokawaModel weights not found in config. Using default weights.
```

### Analysis

The `ToyokawaModel` was initialized using default weights because its configuration weights were not found. While the script proceeded successfully, this might indicate that custom or optimized weights are expected but not provided, potentially affecting the simulation's accuracy or specific behavior.

### Resolution

Ensure that the `ToyokawaModel` configuration file (e.g., `config/toyokawa_model_profile.json` or similar, as suggested by the project structure) contains the necessary weights, or that the script is correctly configured to locate them.
