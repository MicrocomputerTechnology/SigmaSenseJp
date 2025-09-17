import os
import re
# Add the project root to the path to allow importing vetra_llm_core
import sys
sys.path.append('/Users/miyata.fumio/ProjectRealize')
from vetra_llm_core import VetraLLMCore

def main():
    """Main function to understand numbers using the Vetra LLM core."""
    print("--- Temporary Handler: Number Understanding (Vetra Mode) ---")

    # 1. Input data for the learning objective
    input_data = {"numbers": [14, 5, 27, 8, 3]}
    print(f"Input numbers: {input_data['numbers']}")

    # 2. Instantiate Vetra's core
    try:
        vetra = VetraLLMCore()
    except Exception as e:
        print(f"ERROR: Could not initialize VetraLLMCore: {e}")
        # In a real scenario, this would indicate an offline environment issue.
        # For this simulation, we'll print the error and exit.
        return

    # 3. Construct prompts and call the LLM
    system_prompt = "You are a helpful assistant that follows instructions precisely. Analyze the user's request and provide a direct, concise answer."
    user_prompt = f"INPUT: {input_data['numbers']}\nTASK: Find the largest number in the input list.\nOUTPUT:"

    # Use the internal _call_local_llm method as per the plan
    llm_response = vetra._call_local_llm(system_prompt, user_prompt)

    # 4. Parse the response and determine the result
    try:
        # Find the first integer in the response
        found_number = int(re.search(r'\d+', llm_response).group())
        print(f"LLM Response: '{llm_response.strip()}'")
        print(f"Parsed Result: {found_number}")
        
        # Verification
        if found_number == max(input_data['numbers']):
            print("Verification: SUCCESS - LLM correctly identified the largest number.")
        else:
            print("Verification: FAILED - LLM did not identify the largest number.")

    except (AttributeError, ValueError) as e:
        print(f"ERROR: Could not parse a number from the LLM's response: '{llm_response}'")
        print(f"Parsing error: {e}")

    print("\n----------------------------------------------------------")

if __name__ == "__main__":
    main()
