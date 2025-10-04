import sys
import os
import cv2

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sigmasense.temporary_handler_base import BaseHandler

class ImageContourCountHandler(BaseHandler):
    def handle(self, image_path, context):
        """
        画像内の外部輪郭を検出し、その数を返すハンドラ。
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'status': 'failed', 'error': 'Image not found or could not be read.'}

            # グレースケールに変換
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 外部輪郭を検出
            # RETR_EXTERNAL: 最も外側の輪郭のみを検出
            # CHAIN_APPROX_SIMPLE: 輪郭の水平、垂直、斜めのセグメントを圧縮し、端点のみを保存
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 輪郭の数を数える
            num_contours = len(contours)

            return {'status': 'completed', 'num_contours': num_contours}

        except cv2.error as e:
            # OpenCV固有のエラーが発生した場合
            return {'status': 'failed', 'error': f'OpenCV processing error during contour detection: {e}'}
        except Exception as e:
            # その他の予期せぬエラー
            return {'status': 'failed', 'error': f'An unexpected error occurred: {e}'}