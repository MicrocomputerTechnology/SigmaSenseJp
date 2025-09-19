import cv2
import numpy as np

def extract_structure_features(image_path):
    """
    対象物の領域群を抽出する。
    各領域は {"x": ..., "y": ..., "w": ..., "h": ...} の形式。
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []

    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        regions.append({"x": x, "y": y, "w": w, "h": h})

    return regions
