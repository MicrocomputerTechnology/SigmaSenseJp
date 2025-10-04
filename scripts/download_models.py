import os
import subprocess
import tensorflow as tf
import tensorflow_hub as hub
import zipfile
import requests
import shutil

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
EJDICT_URL = "https://github.com/kujirahand/EJDict/archive/refs/heads/master.zip"
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
    """Downloads and extracts the EJDict-hand database with robust error handling."""
    print("\n--- Downloading EJDict-hand ---")
    zip_path = os.path.join(DATA_DIR, "ejdict.zip")
    db_path = os.path.join(DATA_DIR, "ejdict.sqlite3")
    extracted_dir = os.path.join(DATA_DIR, "EJDict-master")
    final_db_path_in_zip = os.path.join(extracted_dir, "ejdict.sqlite3")

    if os.path.exists(db_path):
        print("ejdict.sqlite3 already exists. Skipping download.")
        return

    print(f"Downloading {EJDICT_URL} to {zip_path}...")
    if not download_file(EJDICT_URL, zip_path):
        raise RuntimeError("Failed to download EJDict-hand zip file.")

    try:
        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        print(f"Extracted to {DATA_DIR}.")

        if not os.path.exists(final_db_path_in_zip):
            # Fallback: Check if the structure is different (e.g., nested directory)
            found_db = None
            for root, _, files in os.walk(extracted_dir):
                if "ejdict.sqlite3" in files:
                    found_db = os.path.join(root, "ejdict.sqlite3")
                    break
            if found_db:
                final_db_path_in_zip = found_db
                print(f"Found database at non-standard path: {found_db}")
            else:
                raise FileNotFoundError(f"ejdict.sqlite3 not found in the expected directory: {final_db_path_in_zip}")

        print(f"Moving {final_db_path_in_zip} to {db_path}...")
        os.rename(final_db_path_in_zip, db_path)

        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Failed to move database to {db_path}")
        
        print("Successfully installed ejdict.sqlite3.")

    except Exception as e:
        print(f"An error occurred during EJDict-hand processing: {e}")
        # Raise the exception to ensure CI fails if something goes wrong.
        raise
    finally:
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"Removed temporary file: {zip_path}")
        if os.path.exists(extracted_dir):
            # Use shutil for robust directory removal
            shutil.rmtree(extracted_dir)
            print(f"Removed temporary directory: {extracted_dir}")


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
