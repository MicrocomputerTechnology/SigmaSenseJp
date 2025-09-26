import os
import subprocess
import tensorflow as tf
import tensorflow_hub as hub

# Create models directory if it doesn't exist
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# --- Download TFLite models ---
print("--- Downloading TFLite models ---")

# EfficientNet-Lite0
efficientnet_url = "https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/image_classification/lite-model_efficientnet_lite0_int8_1.tflite"
efficientnet_path = os.path.join(model_dir, "efficientnet_lite0.tflite")
if not os.path.exists(efficientnet_path):
    print(f"Downloading EfficientNet-Lite0 to {efficientnet_path}...")
    try:
        subprocess.run(["curl", "-L", efficientnet_url, "-o", efficientnet_path], check=True)
        print("EfficientNet-Lite0 downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading EfficientNet-Lite0: {e}")
else:
    print(f"EfficientNet-Lite0 already exists at {efficientnet_path}. Skipping download.")

# MobileNet V1
mobilenet_url = "https://storage.googleapis.com/download.tensorflow.org/models/tflite/mobilenet_v1_1.0_224.tflite"
mobilenet_path = os.path.join(model_dir, "mobilenet_v1.tflite")
if not os.path.exists(mobilenet_path):
    print(f"Downloading MobileNet V1 to {mobilenet_path}...")
    try:
        subprocess.run(["curl", "-L", mobilenet_url, "-o", mobilenet_path], check=True)
        print("MobileNet V1 downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading MobileNet V1: {e}")
else:
    print(f"MobileNet V1 already exists at {mobilenet_path}. Skipping download.")


# --- Download SavedModel format models ---
print("\n--- Downloading SavedModel format models ---")

# MobileViT model
mobilevit_path = os.path.join(model_dir, "mobilevit-tensorflow2-xxs-1k-256-v1")
if not os.path.exists(mobilevit_path):
    print("Downloading and saving MobileViT model...")
    mobilevit_url = "https://itb.co.jp/wp-content/uploads/mobilevit-tensorflow2-xxs-1k-256-v1.zip"
    try:
        # Download the zip file
        zip_path = os.path.join(model_dir, "mobilevit-tensorflow2-xxs-1k-256-v1.zip")
        subprocess.run(["curl", "-L", mobilevit_url, "-o", zip_path], check=True)
        print("MobileViT zip downloaded successfully. Extracting...")

        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(mobilevit_path)
        os.remove(zip_path) # Clean up the zip file
        print("MobileViT model extracted successfully.")
    except Exception as e:
        print(f"Error downloading or saving MobileViT model: {e}")
else:
    print(f"MobileViT model already exists at {mobilevit_path}. Skipping download.")


# ResNet V2 50 model
resnet_path = os.path.join(model_dir, "resnet_v2_50_saved_model")
if not os.path.exists(resnet_path):
    print("Downloading and saving ResNet V2 50 model...")
    resnet_url = "https://tfhub.dev/google/imagenet/resnet_v2_50/classification/5"
    try:
        resnet_model = hub.KerasLayer(resnet_url)
        tf.saved_model.save(resnet_model, resnet_path)
        print("ResNet V2 50 model saved successfully.")
    except Exception as e:
        print(f"Error downloading or saving ResNet V2 50 model: {e}")
else:
    print(f"ResNet V2 50 model already exists at {resnet_path}. Skipping download.")


print("\n--- Model download process completed ---")
