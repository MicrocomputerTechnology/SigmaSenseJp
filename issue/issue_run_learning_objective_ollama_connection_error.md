## Error: Ollama Connection Failure in `run_learning_objective.py`

When running `scripts/run_learning_objective.py`, the script failed to connect to the local Ollama server for code generation.

### Error Message

```
--- Calling Local LLM 'codegemma:latest' (Vetra) ---
  - 失敗: コード生成中にエラーが発生しました。
--------------------------------------------------
    エラー: ERROR calling local LLM 'codegemma:latest' via ollama: Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible. https://ollama.com/download
    Please check that Ollama is downloaded, running and accessible. https://ollama.com/download
    Please ensure the Ollama server is running (`ollama serve`)
    and the model 'codegemma:latest' is available (`ollama pull codegemma:latest`).
--------------------------------------------------
```

### Analysis

The script attempts to use a local LLM (`codegemma:latest`) via Ollama for its self-extension cycle (Stage 2: Improvisation). The error indicates that the Ollama server was either not running or the `codegemma:latest` model was not available, preventing the code generation process.

### Resolution (as suggested by script output)

To resolve this, ensure the Ollama server is installed and running (`ollama serve`), and that the `codegemma:latest` model has been pulled (`ollama pull codegemma:latest`).