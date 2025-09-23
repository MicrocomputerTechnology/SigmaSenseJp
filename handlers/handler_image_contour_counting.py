import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporary_handler_base import BaseHandler

class ImageContourCountHandler(BaseHandler):
    """
    画像をグレースケールに変換し、外部輪郭を検出してその数を数えるハンドラ。
    SigmaSenseプロジェクトの設計思想に沿い、堅牢なエラーハンドリングと汎用性を持つ。
    """
    def execute(self, objective: dict) -> dict:
        """
        指定された画像パスから画像を読み込み、輪郭の数を数えて返します。

        Args:
            objective (dict): 処理対象の画像パスを含む辞書。
                              例: {'image_path': '/path/to/image.jpg'}

        Returns:
            dict: 処理結果を示す辞書。
                  成功時: {'status': 'completed', 'num_contours': int}
                  失敗時: {'status': 'failed', 'error': str}
        """
        # 1. 入力値の検証
        if 'image_path' not in objective:
            return {'status': 'failed', 'error': 'Objective dictionary must contain "image_path".'}

        image_path = objective['image_path']

        # 2. 画像の読み込みとエラーハンドリング
        try:
            # cv2ライブラリは実行環境に存在するためimport不要
            image = cv2.imread(image_path)

            if image is None:
                # cv2.imreadがNoneを返す場合、画像ファイルが存在しないか、読み込めない形式である
                return {'status': 'failed', 'error': f'Could not read image from path: "{image_path}". '
                                                      'Please ensure the file exists and is a valid image format.'}
        except Exception as e:
            # 画像読み込み中に予期せぬエラーが発生した場合
            return {'status': 'failed', 'error': f'An unexpected error occurred during image loading: {e}'}

        # 3. 画像処理とエラーハンドリング
        try:
            # グレースケールに変換
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # 外部輪郭を検出
            # RETR_EXTERNAL: 最も外側の輪郭のみを検出
            # CHAIN_APPROX_SIMPLE: 輪郭の水平、垂直、斜めのセグメントを圧縮し、端点のみを保存
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 輪郭の数を数える
            num_contours = len(contours)

            # 処理結果を返す
            return {'status': 'completed', 'num_contours': num_contours}

        except cv2.error as e:
            # OpenCV固有のエラーが発生した場合
            return {'status': 'failed', 'error': f'OpenCV processing error during contour detection: {e}'}
        except Exception as e:
            # 画像処理中に予期せぬエラーが発生した場合
            return {'status': 'failed', 'error': f'An unexpected error occurred during image processing: {e}'}

