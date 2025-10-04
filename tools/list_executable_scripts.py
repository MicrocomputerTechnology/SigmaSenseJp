
from collections import defaultdict

# Scripts manually registered in .github/workflows/main.yml and .github/workflows/run-scripts.yml
CI_REGISTERED_SCRIPTS = [
    # from main.yml
    "scripts/download_models.py",
    "src/build_database.py",
    
    # from run-scripts.yml
    "scripts/run_sigma.py",
    "scripts/run_learning_objective.py",
    "scripts/run_sheaf_analysis.py",
    "tools/functor_consistency_checker.py",
    "src/stabilize_database.py",
    "scripts/run_ethics_check_on_text.py",
    "scripts/run_narrative_analysis.py",
    "src/generate_number_image.py",
    "src/generate_ai_image_vectors.py",
    "src/generate_ai_dimensions.py",
    "scripts/run_terrier_comparison.py",
    "scripts/run_psyche_simulation.py",
]

def categorize_script(script_path):
    """Categorizes a script based on its path and name."""
    script_path = script_path.lower()
    
    # Category keywords
    core_execution = ['run_sigma', 'run_learning_objective', 'run_online_integration']
    db_models = ['database', 'model', 'stabilize']
    analysis = ['benchmark', 'ethics', 'analysis', 'report', 'comparison', 'evaluator', 'sheaf']
    dev_tools = ['check', 'functor', 'tool', 'review', 'list_executable']
    generation = ['experiment', 'generate', 'simulation', 'narrative']

    if any(keyword in script_path for keyword in core_execution):
        return "1. Core System Execution"
    if any(keyword in script_path for keyword in db_models):
        return "2. Database & Model Management"
    if any(keyword in script_path for keyword in analysis):
        return "3. Analysis & Evaluation"
    if any(keyword in script_path for keyword in dev_tools):
        return "4. Development & Maintenance Tools"
    if any(keyword in script_path for keyword in generation):
        return "5. Experimentation & Data Generation"
    
    return "6. Uncategorized"

def get_categorized_scripts():
    """Categorizes the predefined list of CI-registered scripts."""
    categorized_scripts = defaultdict(list)
    unique_scripts = sorted(list(set(CI_REGISTERED_SCRIPTS)))
    
    for script_path in unique_scripts:
        category = categorize_script(script_path)
        categorized_scripts[category].append(script_path)
    
    return categorized_scripts

if __name__ == "__main__":
    categorized_scripts = get_categorized_scripts()
    
    print("=================================================================")
    print("  Scripts Registered in Manual CI Workflows (main & run-scripts)")
    print("=================================================================")
    
    if categorized_scripts:
        for category in sorted(categorized_scripts.keys()):
            print(f"\n--- {category} ---")
            for script in sorted(categorized_scripts[category]):
                print(f"- {script}")
    else:
        print("No scripts are registered in the manual CI workflows.")
