from temporary_handler_base import BaseHandler

class RepetitionHandler(BaseHandler):
    def execute(self, narrative: dict) -> dict:
        print('臨時ハンドラ内のprint文が安全に実行されました。')
        return {"status": "interpreted", "processed_content": narrative.get("content", "") * 2}
