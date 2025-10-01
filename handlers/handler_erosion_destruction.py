import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sigmasense.temporary_handler_base import BaseHandler

class ErosionHandler(BaseHandler):
    def execute(self, narrative: dict) -> dict:
        return {"status": "interpreted", "processed_content": "...無になった..."}
