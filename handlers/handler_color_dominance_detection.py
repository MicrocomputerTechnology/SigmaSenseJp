import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sigmasense.temporary_handler_base import BaseHandler
import cv2
import numpy as np

class ColorDominanceHandler(BaseHandler):
    def execute(self, objective: dict) -> dict:
        image_path = 'sigma_images/circle_center_red.jpg'
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'status': 'error', 'message': 'Image not found'}
            means = np.mean(img, axis=(0, 1))
            dominant_channel_idx = np.argmax(means)
            colors = ['Blue', 'Green', 'Red']
            dominant_color = colors[dominant_channel_idx]
            return {'status': 'interpreted', 'result': f'Dominant color is {dominant_color}', 'details': {'b_mean': means[0], 'g_mean': means[1], 'r_mean': means[2]}}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}