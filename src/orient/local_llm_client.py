class LocalLLMClient:
    def __init__(self, model_name: str = "llama3-8b"):
        pass

    def query_text(self, prompt: str, system_prompt: str = "") -> str:
        pass

    def query_multimodal(self, prompt_parts: list) -> str:
        pass
