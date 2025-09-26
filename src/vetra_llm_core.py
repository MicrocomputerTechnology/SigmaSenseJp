import yaml
import os
import json
import ollama

class VetraLLMCore:
    """
    Vetra's LLM core, capable of generating both narratives and code.
    It uses specific local LLMs via 'ollama' for different tasks:
    - Narrative Model: For explaining semantic dimensions and comparisons.
    - Code Generation Model: For creating temporary handlers from task descriptions.
    """

    def __init__(self, config_path="vector_dimensions_mobile.yaml", 
                 narrative_model="lucas2024/gemma-2-2b-jpn-it:q8_0", 
                 code_gen_model="codegemma:latest"):
        """
        Initializes Vetra's core.
        """
        print("VetraLLMCore initializing...")
        self.narrative_model = narrative_model
        self.code_gen_model = code_gen_model
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print("VetraLLMCore: Dimension config loaded.")
            print(f"VetraLLMCore: Narrative model set to '{self.narrative_model}'.")
            print(f"VetraLLMCore: Code generation model set to '{self.code_gen_model}'.")
        except FileNotFoundError:
            print(f"VetraLLMCore: Config file not found at {config_path}.")
            self.config = {}
        except Exception as e:
            print(f"An error occurred during VetraLLMCore init: {e}")

    def _call_local_llm(self, model, system_prompt, user_prompt):
        """
        Calls the specified local LLM using the ollama library.
        Returns a tuple (response_content, error_message).
        """
        try:
            print(f"\n--- Calling Local LLM '{model}' (Vetra) ---")
            response = ollama.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
            )
            print("--- LLM Response Received ---")
            return response['message']['content'], None
        except Exception as e:
            error_message = (
                f"ERROR calling local LLM '{model}' via ollama: {e}\n"
                f"Please check that Ollama is downloaded, running and accessible. https://ollama.com/download\n"
                f"Please ensure the Ollama server is running (`ollama serve`)\n"
                f"and the model '{model}' is available (`ollama pull {model}`)."
            )
            return None, error_message

    def explain_vector(self, vector):
        """
        Generates a natural language explanation of an image's vector.
        """
        system_prompt = "あなたは、画像分析AI「ヴェトラ」です。観測された特徴ベクトルから、画像の特性を簡潔に、1〜2文で日本語で説明してください。"
        user_prompt = f"""
        以下の特徴ベクトルを持つ画像について説明してください。
        ```json
        {json.dumps(vector, indent=2, ensure_ascii=False)}
        ```
        """
        return self._call_local_llm(self.narrative_model, system_prompt, user_prompt)

    def explain_similarity(self, vector1, vector2, similarity_score, hint=None):
        """
        Explains why two vectors are similar or dissimilar, guided by a hint.
        """
        if hint and 'prompt_hint' in hint:
            base_prompt = "あなたは、画像分析AI「ヴェトラ」です。"
            system_prompt = f"{base_prompt} {hint['prompt_hint']}"
        else:
            system_prompt = "あなたは、画像分析AI「ヴェトラ」です。2つの画像から得られた特徴ベクトルと、その類似度スコアを分析し、それらがどの程度似ているか、またその結論に至った根拠となる特徴は何かを、日本語で簡潔に説明してください。"

        user_prompt = f"""
        以下のデータに基づいて、2つの画像の類似性を分析・説明してください。
        - 画像1のベクトル:
        ```json
        {json.dumps(vector1, indent=2, ensure_ascii=False)}
        ```
        - 画像2のベクトル:
        ```json
        {json.dumps(vector2, indent=2, ensure_ascii=False)}
        ```
        - 算出された類似度スコア: {similarity_score:.4f}
        """
        return self._call_local_llm(self.narrative_model, system_prompt, user_prompt)

    def generate_handler_code(self, task_description):
        """
        Generates a temporary handler Python code from a task description.
        """
        system_prompt = """
        You are an expert Python programmer specializing in the SigmaSense project.
        Your task is to generate a Python script for a 'temporary_handler' based on a user's request.
        The script must follow these rules:
        1.  It must be a complete, self-contained Python script.
        2.  It must define a class that inherits from `BaseHandler`.
        3.  This class must implement an `execute(self, objective: dict) -> dict` method.
        4.  The `execute` method can use `cv2` and other safe libraries.
        5.  The script MUST NOT import any modules. `cv2` and `BaseHandler` are already available.
        6.  The final output should be ONLY the Python code, enclosed in ```python ... ```.
        """
        # Using string concatenation to avoid f-string issues with curly braces
        user_prompt = (
            "Please generate a temporary handler script for the following task:\n"
            f'\"{task_description}\"\n\n'
            "Example of a valid handler structure:\n"
            "```python\n"
            "import cv2\n"
            "\n"
            "def handle(image_path, dimension_generator):\n"
            "    # Your processing logic here\n"
            "    # Example: Get a specific feature\n"
            "    # brightness = dimension_generator.get_feature('brightness', image_path)\n"
            "    \n"
            "    result = {'status': 'completed', 'message': 'Describe your findings here.'}\n"
            "    return result\n"
            "```"
        )
        
        raw_response, error = self._call_local_llm(self.code_gen_model, system_prompt, user_prompt)
        
        if error:
            return f"エラー: {error}"

        # Extract code from the markdown block
        if "```python" in raw_response:
            code = raw_response.split("```python")[1].split("```")[0].strip()
            return code
        else:
            # If no markdown block is found, return the raw response and let the caller handle it
            return raw_response

    def propose_new_dimension(self, features: dict):
        """
        Generates a new dimension definition based on a set of unexplainable features.
        """
        system_prompt = """
        You are an expert AI analyst specializing in the SigmaSense project.
        Your task is to define a new semantic dimension based on a set of raw features from an image.
        The new dimension should capture a meaningful, abstract concept that these features might represent.
        You must return a single JSON object with the following keys: 'id', 'name_ja', 'description', 'algorithm_idea'.
        - 'id': A concise, snake_case identifier (e.g., 'texture_complexity').
        - 'name_ja': A short, descriptive Japanese name (e.g., 'テクスチャの複雑さ').
        - 'description': A brief explanation of what this dimension measures.
        - 'algorithm_idea': A high-level description of how one might compute this value from an image using OpenCV or similar libraries.
        The output must be ONLY the JSON object, enclosed in ```json ... ```.
        """
        
        user_prompt = (
            "Based on the following raw feature vector, propose a new semantic dimension that could explain these values.\n"
            f'```json\n{json.dumps(features, indent=2)}\n```\n'
        )

        raw_response, error = self._call_local_llm(self.code_gen_model, system_prompt, user_prompt)

        if error:
            return {"error": error}

        # Extract JSON from the markdown block
        try:
            if "```json" in raw_response:
                json_str = raw_response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                # Attempt to parse the whole string if no markdown is found
                return json.loads(raw_response)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse LLM response as JSON: {e}", "raw_response": raw_response}
        except Exception as e:
            return {"error": f"An unexpected error occurred during parsing: {e}", "raw_response": raw_response}


if __name__ == '__main__':
    print("--- Running Vetra's REAL LLM Core ---")
    
    # Initialize with default models
    vetra = VetraLLMCore()
    
    # --- Test 1: Narrative Generation (High similarity) ---
    print("\n--- Test 1: Narrative Generation (High similarity) ---")
    vec1 = {'yolo_object_count': 3, 'opencv_edge_density': 0.1}
    vec2 = {'yolo_object_count': 3, 'opencv_edge_density': 0.12}
    sim_score1 = 0.95
    hint1 = {'prompt_hint': '2つの画像は非常に似ています。まず類似度が高いことを述べた上で、完全には一致しない理由として、両者の間の最も細かい違いを特定して説明してください。'}
    explanation1 = vetra.explain_similarity(vec1, vec2, sim_score1, hint1)
    print(f"\n[Vetra's Narrative Analysis]\n{explanation1}")

    # --- Test 2: Code Generation ---
    print("\n--- Test 2: Code Generation ---")
    task_desc = "Analyze the input image to determine if it contains a dog. Use the 'dog_breed_confidence' feature from the dimension_generator. If the confidence is above 0.5, return a success message, otherwise return a failure message."
    generated_code = vetra.generate_handler_code(task_desc)
    print(f"\n[Vetra's Generated Code]\n```python\n{generated_code}\n```")

    # --- Test 3: Another Code Generation Example ---
    print("\n--- Test 3: Another Code Generation Example ---")
    task_desc_2 = "Count the number of contours in the image using OpenCV and return the count."
    generated_code_2 = vetra.generate_handler_code(task_desc_2)
    print(f"\n[Vetra's Generated Code]\n```python\n{generated_code_2}\n```")