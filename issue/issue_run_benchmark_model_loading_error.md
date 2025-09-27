## Error: Model Loading and Configuration Issues in `run_benchmark.py`

When running `scripts/run_benchmark.py`, several errors and warnings related to model loading and configuration were observed, despite the script completing execution.

### Errors

1.  **EfficientNet-Lite TFLite Model Loading Failure:**
    ```
    !!! ERROR: Failed to load TFLite model at models/efficientnet_lite0.tflite !!!
    Error: Model provided has model identifier '<!DO', should be 'TFL3'
    ```
    This indicates that the `efficientnet_lite0.tflite` model file is either corrupted or not a valid TFLite model, or there's an issue with its format.

2.  **ResNet V2 50 SavedModel Loading Failure:**
    ```
    !!! ERROR: Failed to load SavedModel from models/resnet_v2_50_saved_model !!!
    Error: 'serving_default'
    ```
    This suggests an issue with loading the `resnet_v2_50_saved_model` SavedModel, possibly due to a missing 'serving_default' signature or a corrupted model directory.

### Warnings

1.  **Main Database Not Found:**
    ```
    Warning: Main database not found. Proceeding with empty DB for ethics check.
    ```
    The script proceeded with an empty database, which might affect the ethics check results.

2.  **PersonalMemoryGraph Config File Not Found:**
    ```
    Warning: PersonalMemoryGraph config file not found or invalid at /sdcard/project/SigmaSenseJp/sigma_logs/personal_memory.jsonl. Using default memory path.
    ```
    The `personal_memory.jsonl` file was not found, leading to the use of a default memory path.

3.  **GiNZA Model Not Found (GrowthTracker and MeaningAxisDesigner):**
    ```
    GrowthTracker: GiNZA model not found. Please run 'python -m spacy download ja_ginza'
    MeaningAxisDesigner: GiNZA model not found. Please run 'python -m spacy download ja_ginza'
    ```
    The `ja_ginza` spaCy model, required by `GrowthTracker` and `MeaningAxisDesigner`, was not found. This will impact functionalities relying on natural language processing.

4.  **Deprecated TensorFlow Lite Interpreter:**
    ```
    /root/venv/lib/python3.12/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
    TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
    See the [migration guide](https://ai.google.dev/edge/litert/migration)
    for details.
    ```
    This is a deprecation warning from TensorFlow Lite, indicating that the `tf.lite.Interpreter` API is outdated and should be migrated to `LiteRT`.

### Resolution

-   Ensure all required TFLite and SavedModel files are correctly downloaded and are valid. Refer to the "機械学習モデルの準備" section in `README.md`.
-   Verify the presence and correctness of `config/sigma_product_database_custom_ai_generated.json` and `sigma_logs/personal_memory.jsonl`.
-   Install the `ja_ginza` spaCy model by running `python -m spacy download ja_ginza`.
-   Consider updating TensorFlow Lite API usage to `LiteRT` to address the deprecation warning.