import os
import re
import json
import google.generativeai as genai
from PIL import Image

class GeminiClient:
    """
    Google Gemini APIと通信を行うクライアント。
    テキストモデルとマルチモーダルモデルの両方に対応する。
    """
    def __init__(self):
        """
        環境変数からAPIキーを読み込んでクライアントを初期化する。
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("環境変数 'GEMINI_API_KEY' が設定されていません。")
        
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel('gemini-2.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ GeminiClientが初期化され、テキスト・ビジョンモデルの準備ができました。")

    def _parse_response(self, response_text):
        """
        応答テキストからJSONブロックを抽出し、パースする。
        リスト形式、オブジェクト形式の両方に対応し、Markdownブロックも考慮する。
        パースに成功すればJSONオブジェクトを、失敗すればクリーンなテキストを返す。
        """
        # 1. 正規表現で ```json ... ``` ブロックを探す (リストとオブジェクトの両方に対応)
        match = re.search(r"```json\s*(\[.*?\]|\{.*?\})\s*```", response_text, re.DOTALL)
        
        json_text = ""
        if match:
            # マッチすれば、その中身をJSONテキストとする
            json_text = match.group(1)
        else:
            # 2. マッチしない場合、手動でマーカーを除去しようと試みる
            json_text = response_text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]

        try:
            # 3. 抽出したテキストをJSONとしてパースして返す
            return json.loads(json_text)
        except json.JSONDecodeError:
            # 4. それでもパースに失敗した場合、呼び出し元で処理できるよう、
            #    クリーンにしたテキストそのものを返す
            print(f"⚠️  JSONパースに失敗しました。クリーンなテキストを返します。応答テキスト: {json_text}")
            return json_text # パース失敗時はクリーンなテキストを返す

    def query_text(self, prompt):
        """
        テキストプロンプトをAPIに送信し、レスポンスを返す。
        パースされたJSONオブジェクト、またはクリーンなテキスト文字列を返す。
        """
        print(f"   - (Text) APIにクエリを送信中...")
        try:
            response = self.text_model.generate_content(prompt)
            # _parse_responseはパースされたオブジェクトか、クリーンなテキストを返す
            return self._parse_response(response.text)
        except Exception as e:
            print(f"❗ APIクエリ中に予期せぬエラーが発生しました: {e}")
            return None # API通信自体のエラーの場合はNoneを返す

    def query_multimodal(self, prompt_parts):
        """
        画像とテキストを含むマルチモーダルなプロンプトをAPIに送信し、JSONレスポンスを返す。
        prompt_parts: [Image, "text", Image, "text", ...] の形式のリスト
        """
        print(f"   - (Vision) APIにクエリを送信中...")
        try:
            response = self.vision_model.generate_content(prompt_parts)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"❗ APIクエリ中に予期せぬエラーが発生しました: {e}")
            return None
