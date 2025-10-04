import os
import re
import json
import google.generativeai as genai
import google.api_core.exceptions
from src.vetra.vetra_llm_core import VetraLLMCore

class GeminiClient:
    """
    Google Gemini APIと通信を行うクライアント。
    テキストモデルとマルチモーダルモデルの両方に対応する。
    API障害時には、ローカルLLMへのフォールバック機能を備える。
    """
    def __init__(self, config_path="config/orient_profile.json"):
        """
        設定ファイルを読み込み、APIキーを環境変数から取得してクライアントを初期化する。
        フォールバック用のローカルLLMも準備する。
        """
        # APIキーの設定
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("環境変数 'GEMINI_API_KEY' が設定されていません。")
        genai.configure(api_key=api_key)

        # 設定ファイルの読み込み
        self.gemini_model_name = 'gemini-2.5-flash' # デフォルト値
        self.fallback_model_name = None
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.gemini_model_name = config.get('gemini_model', self.gemini_model_name)
                self.fallback_model_name = config.get('fallback_local_model')

        # Geminiモデルの初期化
        self.text_model = genai.GenerativeModel(self.gemini_model_name)
        self.vision_model = genai.GenerativeModel(self.gemini_model_name)
        print(f"✅ GeminiClientが初期化され、プライマリモデル '{self.gemini_model_name}' の準備ができました。")

        # フォールバック用ローカルLLMの初期化
        self.fallback_llm = None
        if self.fallback_model_name:
            print(f"   - フォールバックモデル '{self.fallback_model_name}' を準備中...")
            try:
                # Vetraのコアを、オリエンのフォールバック用にインスタンス化
                self.fallback_llm = VetraLLMCore(
                    code_gen_model=self.fallback_model_name, 
                    hf_fallback_model_name=self.fallback_model_name
                )
                print(f"✅ フォールバック用のローカルLLM '{self.fallback_model_name}' が準備できました。")
            except Exception as e:
                print(f"❗ フォールバック用ローカルLLMの初期化に失敗しました: {e}")
                self.fallback_llm = None


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

    def query_text(self, prompt, system_prompt="You are a helpful assistant."):
        """
        テキストプロンプトをAPIに送信し、レスポンスを返す。
        API呼び出しに失敗した場合、ローカルLLMにフォールバックする。
        """
        print("   - (Text) プライマリAPIにクエリを送信中...")
        try:
            response = self.text_model.generate_content(prompt)
            return self._parse_response(response.text)
        except (google.api_core.exceptions.GoogleAPICallError, Exception) as e:
            print(f"❗ プライマリAPIクエリ中にエラーが発生しました: {e}")
            
            if self.fallback_llm:
                print(f"   - ローカルLLM '{self.fallback_model_name}' にフォールバックします...")
                try:
                    response_content, error_message = self.fallback_llm._call_local_llm(
                        model=self.fallback_model_name,
                        system_prompt=system_prompt,
                        user_prompt=prompt
                    )
                    if error_message:
                        print(f"❗ ローカルLLMへのフォールバック中にエラーが発生しました: {error_message}")
                        return None
                    
                    return self._parse_response(response_content)
                except Exception as fallback_e:
                    print(f"❗ ローカルLLMへのフォールバック中に予期せぬエラーが発生しました: {fallback_e}")
                    return None
            else:
                print("❗ フォールバックLLMが利用できないため、処理を中断します。")
                return None

    def query_multimodal(self, prompt_parts):
        """
        画像とテキストを含むマルチモーダルなプロンプトをAPIに送信し、JSONレスポンスを返す。
        prompt_parts: [Image, "text", Image, "text", ...] の形式のリスト
        NOTE: このメソッドは現在ローカルLLMへのフォールバックをサポートしていません。
        """
        print("   - (Vision) APIにクエリを送信中...")
        try:
            response = self.vision_model.generate_content(prompt_parts)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"❗ APIクエリ中に予期せぬエラーが発生しました: {e}")
            return None