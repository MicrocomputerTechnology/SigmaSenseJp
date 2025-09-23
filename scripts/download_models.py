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
efficientnet_url = "https://tfhub.dev/tensorflow/efficientnet/lite0/classification/2?tf-hub-format=tflite"
efficientnet_path = os.path.join(model_dir, "efficientnet_lite0.tflite")
print(f"Downloading EfficientNet-Lite0 to {efficientnet_path}...")
try:
    subprocess.run(["curl", "-L", efficientnet_url, "-o", efficientnet_path], check=True)
    print("EfficientNet-Lite0 downloaded successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error downloading EfficientNet-Lite0: {e}")

# MobileNet V1
mobilenet_url = "https://tfhub.dev/tensorflow/lite-model/mobilenet_v1_1.0_224/1/default/1?lite-format=tflite"
mobilenet_path = os.path.join(model_dir, "mobilenet_v1.tflite")
print(f"Downloading MobileNet V1 to {mobilenet_path}...")
try:
    subprocess.run(["curl", "-L", mobilenet_url, "-o", mobilenet_path], check=True)
    print("MobileNet V1 downloaded successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error downloading MobileNet V1: {e}")

# --- Download SavedModel format models ---
print("\n--- Downloading SavedModel format models ---")

# MobileViT model
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
        zip_ref.extractall(os.path.join(model_dir, "mobilevit-tensorflow2-xxs-1k-256-v1"))
    os.remove(zip_path) # Clean up the zip file
    print("MobileViT model extracted successfully.")
except Exception as e:
    print(f"Error downloading or saving MobileViT model: {e}")

# ResNet V2 50 model
print("Downloading and saving ResNet V2 50 model...")
resnet_url = "https://www.kaggle.com/models/google/resnet-v2/TensorFlow2/50-classification/2"
try:
    resnet_model = hub.KerasLayer(resnet_url)
    tf.saved_model.save(resnet_model, os.path.join(model_dir, "resnet_v2_50_saved_model"))
    print("ResNet V2 50 model saved successfully.")
except Exception as e:
    print(f"Error downloading or saving ResNet V2 50 model: {e}")

print("\n--- Model download process completed ---")
