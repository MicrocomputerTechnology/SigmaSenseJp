```python
class ImageContourCountHandler(BaseHandler):
    """
    画像を解析し、主要な外部輪郭の数をカウントするハンドラ。
    主に、画像内の明確なオブジェクト（例：数字や記号）の数を識別するために使用されます。
    """
    def execute(self, objective: dict) -> dict:
        """
        指定された画像パスから画像を読み込み、グレースケール変換後、
        外部輪郭を検出してその数をカウントします。

        Args:
            objective (dict): 処理に必要な情報を含む辞書。
                              'image_path'キーに画像ファイルへのパスが含まれていることを期待します。

        Returns:
            dict: 処理結果を示す辞書。
                  成功時には'status': 'completed' と 'contour_count' (輪郭数)、
                  失敗時には'status': 'failed' と 'error_message' を含みます。
        """
        image_path = objective.get('image_path')

        if not image_path:
            return {
                'status': 'failed',
                'error_message': 'objectiveに\'image_path\'が指定されていません。'
            }

        try:
            # 画像を読み込む
            # cv2ライブラリは実行環境に既に存在するため、ここではimportしません。
            image = cv2.imread(image_path)

            # 画像が正常に読み込まれたか確認
            if image is None:
                return {
                    'status': 'failed',
                    'error_message': f'画像パス\'{image_path}\'からの画像読み込みに失敗しました。ファイルが存在し、有効な画像形式であることを確認してください。'
                }

            # グレースケールに変換
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 輪郭を見つける
            # RETR_EXTERNALは最も外側の輪郭のみを検出し、
            # CHAIN_APPROX_SIMPLEは輪郭の冗長な点を圧縮します。
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 輪郭の数をカウント
            contour_count = len(contours)

            return {
                'status': 'completed',
                'contour_count': contour_count,
                'message': f'画像から{contour_count}個の外部輪郭を正常にカウントしました。'
            }

        except Exception as e:
            # 予期せぬエラーをキャッチし、エラーメッセージを返す
            return {
                'status': 'failed',
                'error_message': f'画像処理中に予期せぬエラーが発生しました: {str(e)}'
            }
