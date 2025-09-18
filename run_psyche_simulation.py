
import time
import os
from psyche_logger import PsycheLogger
from toyokawa_model import ToyokawaModel
from sigma_reactor import SigmaReactor

def print_grand_header():
    """Prints the main header for the simulation."""
    os.system('clear' if os.name != 'nt' else 'cls')
    print("=" * 70)
    print("===" + " " * 64 + "===")
    print("===  SigmaSense Ninth Experiment: Group Psyche Matching" + " " * 11 + "===")
    print("===" + " " * 64 + "===")
    print("=" * 70)
    print("\nThis simulation will run through the following phases:")
    print("1. Generate a simulated log of the Octa agents' conversation.")
    print("2. Calculate the group psychological state C(t) for each time step.")
    print("3. Display SigmaSense's reaction to the evolving state.")
    print("-" * 70)
    # The interactive prompt has been removed to allow for non-interactive execution.
    print("Starting simulation automatically...")

if __name__ == '__main__':
    print_grand_header()

    # --- Phase 1: Generate Data ---
    logger = PsycheLogger()
    logger.generate_log()

    # --- Phase 2: Analyze Data ---
    model = ToyokawaModel()
    analysis_results = model.run_analysis()

    # --- Phase 3: React to States ---
    reactor = SigmaReactor()
    
    if analysis_results:
        print("\n" + "="*70)
        print("=== BEGINNING REAL-TIME REACTION SIMULATION ===")
        print("="*70)
        
        try:
            for result in analysis_results:
                t = result['t']
                c_value = result['C(t)']
                state = result['state']
                
                print(f"\n\n>>> Time Step t={t} <<<")
                reaction_description = reactor.generate_reaction(state, c_value)
                print(reaction_description)
                time.sleep(1.5) # Pause for dramatic effect

            print("\n" + "="*70)
            print("=== SIMULATION COMPLETE ===")
            print("="*70)

        except KeyboardInterrupt:
            print("\n\nSimulation interrupted by user.")

    else:
        print("\nSimulation could not run as analysis results were not generated.")
