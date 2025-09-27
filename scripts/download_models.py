import os
import subprocess
import tensorflow as tf
import tensorflow_hub as hub
import zipfile
import requests # Use requests for more robust downloads

# --- Configuration ---
MODEL_DIR = "models"

# Models to download via requests
TFLITE_MODELS = {
    "efficientnet_lite0.tflite": "https://tfhub.dev/tensorflow/lite-model/efficientnet/lite0/int8/1",
    "mobilenet_v1.tflite": "https://tfhub.dev/tensorflow/lite-model/mobilenet_v1_1.0_224/1/default/1?lite-format=tflite"
}

# Models to download via TensorFlow Hub
SAVED_MODELS = {
    "resnet_v2_50_saved_model": "https://www.kaggle.com/models/google/resnet-v2/TensorFlow2/50-classification/2"
}

# Special case for MobileViT (download from zip)
MOBILEVIT_ZIP_URL = "https://itb.co.jp/wp-content/uploads/mobilevit-tensorflow2-xxs-1k-256-v1.zip"
MOBILEVIT_DIR_NAME = "mobilevit-tensorflow2-xxs-1k-256-v1"

# --- Main script ---
def download_file(url, filepath):
    """Downloads a file from a URL to a given path using requests."""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status() # Raise an exception for bad status codes
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        # Basic validation: check if file size is reasonable (e.g., > 1KB)
        if os.path.getsize(filepath) < 1024:
            print(f"WARNING: Downloaded file {filepath} is very small. It might be an error page.")
        print(f"Successfully downloaded {os.path.basename(filepath)}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download {os.path.basename(filepath)}: {e}")
        return False

def main():
    """Downloads all necessary models for the project."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    # --- Download TFLite models ---
    print("--- Downloading TFLite models ---")
    for filename, url in TFLITE_MODELS.items():
        filepath = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            download_file(url, filepath)
        else:
            print(f"{filename} already exists. Skipping.")

    # --- Download SavedModel format models from TF Hub ---
    print("\n--- Downloading SavedModel format models from TensorFlow Hub ---")
    for dirname, url in SAVED_MODELS.items():
        dirpath = os.path.join(MODEL_DIR, dirname)
        if not os.path.exists(dirpath):
            print(f"Downloading and saving {dirname}...")
            try:
                model_layer = hub.KerasLayer(url)
                tf.saved_model.save(model_layer, dirpath)
                print(f"Successfully saved {dirname}.")
            except Exception as e:
                print(f"ERROR: Failed to download or save {dirname}: {e}")
        else:
            print(f"{dirname} already exists. Skipping.")

    # --- Download MobileViT from Zip ---
    print("\n--- Downloading MobileViT model from Zip ---")
    mobilevit_path = os.path.join(MODEL_DIR, MOBILEVIT_DIR_NAME)
    if not os.path.exists(mobilevit_path):
        print(f"Downloading and extracting {MOBILEVIT_DIR_NAME}...")
        zip_path = os.path.join(MODEL_DIR, f"{MOBILEVIT_DIR_NAME}.zip")
        if download_file(MOBILEVIT_ZIP_URL, zip_path):
            try:
                print("Zip file downloaded. Extracting...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(MODEL_DIR)
                print(f"Successfully extracted {MOBILEVIT_DIR_NAME}.")
            except Exception as e:
                print(f"ERROR: Failed to extract {MOBILEVIT_DIR_NAME}: {e}")
            finally:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
    else:
        print(f"{MOBILEVIT_DIR_NAME} already exists. Skipping.")

    print("\n--- Model download process completed ---")

if __name__ == "__main__":
    main()