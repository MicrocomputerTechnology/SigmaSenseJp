import os
import subprocess
import tensorflow as tf
import tensorflow_hub as hub
import zipfile
import requests


# --- Configuration ---
MODEL_DIR = "models"
DATA_DIR = "data"

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

# Dictionaries
WNJPN_URL = "https://github.com/bond-lab/wnja/releases/download/v1.1/wnjpn.db.gz"

# --- Helper Functions ---
def download_file(url, filepath):
    """Downloads a file from a URL to a given path using requests."""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        if os.path.getsize(filepath) < 1024:
            print(f"WARNING: Downloaded file {filepath} is very small. It might be an error page.")
        print(f"Successfully downloaded {os.path.basename(filepath)}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download {os.path.basename(filepath)}: {e}")
        return False

# --- Download Functions ---
def download_tflite_models():
    """Downloads TFLite models."""
    print("--- Downloading TFLite models ---")
    for filename, url in TFLITE_MODELS.items():
        filepath = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            download_file(url, filepath)
        else:
            print(f"{filename} already exists. Skipping.")

def download_saved_models():
    """Downloads SavedModel format models from TensorFlow Hub."""
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

def download_mobilevit_model():
    """Downloads and extracts the MobileViT model."""
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

def download_ejdict():
    """Downloads the EJDict-hand database directly as a sqlite3 file."""
    print("\n--- Downloading EJDict-hand ---")
    db_path = os.path.join(DATA_DIR, "ejdict.sqlite3")
    
    if os.path.exists(db_path):
        print("ejdict.sqlite3 already exists. Skipping download.")
        return

    # This URL provides the pre-converted sqlite3 file
    ejdict_sqlite_url = "https://kujirahand.com/web-tools/EJDictFreeDL.php?key=e924bf30fe04fdf45dac553182e525a5&type=1"

    print(f"Downloading ejdict.sqlite3 from {ejdict_sqlite_url}...")
    if not download_file(ejdict_sqlite_url, db_path):
        raise RuntimeError("Failed to download ejdict.sqlite3 file.")
    
    if os.path.exists(db_path):
        print("Successfully installed ejdict.sqlite3.")
    else:
        raise FileNotFoundError("ejdict.sqlite3 not found after download.")


def download_wnjpn():
    """Downloads and extracts the Japanese WordNet database."""
    print("\n--- Downloading Japanese WordNet (wnjpn) ---")
    gz_path = os.path.join(DATA_DIR, "wnjpn.db.gz")
    db_path = os.path.join(DATA_DIR, "wnjpn.db")

    if os.path.exists(db_path):
        print("wnjpn.db already exists. Skipping download.")
        return

    try:
        print(f"Downloading {WNJPN_URL}...")
        subprocess.run(["wget", WNJPN_URL, "-O", gz_path], check=True)
        print("Download complete. Extracting...")
        subprocess.run(["gunzip", gz_path], check=True)
        print("Successfully downloaded and extracted wnjpn.db.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download or extract wnjpn.db: {e}")
    except FileNotFoundError:
        print("wget or gunzip command not found. Please install them or download the dictionary manually.")

if __name__ == '__main__':
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    download_tflite_models()
    download_saved_models()
    download_mobilevit_model()
    download_ejdict()
    download_wnjpn()

    print("\n--- Asset download process completed ---")
