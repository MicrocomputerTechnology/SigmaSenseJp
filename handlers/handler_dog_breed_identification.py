import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporary_handler_base import BaseHandler

class DogBreedIdentifier(BaseHandler):
    def execute(self, objective: dict) -> dict:
        print("  [ダミーハンドラ] 犬種を識別中...")
        return {
            "status": "interpreted",
            "result": "識別成功（シミュレーション）",
            "confidence": 0.95
        }
