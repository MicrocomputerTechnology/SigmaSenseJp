import json
import argparse
import sys
from orient.gemini_client import GeminiClient

# Selia軸（構造）生成用のプロンプト
prompt_selia = '''
あなたは、画像認識システム「SigmaSense」の設計者です。
これから、単純な幾何学的図形（円、四角、星、線など）の形状、色、位置、組み合わせを比較・照合するための、新しい意味次元を設計してください。

要件は以下の通りです。
1.  次元の数は15〜20個程度とします。
2.  各次元は、PythonのOpenCVライブラリを使って具体的なアルゴリズムで計算可能である必要があります。
3.  「物語性」のような、画像処理での実装が困難な抽象的すぎる概念は避けてください。
4.  出力は、JSON形式のリストとしてください。
5.  リストの各要素は、必ず以下のキーを持つJSONオブジェクトでなければなりません。
    - `id`: 次元の一意なID（英語、snake_case）
    - `name_ja`: 日本語の次元名
    - `description`: 次元が何を表すかの簡単な説明
    - `algorithm_idea`: その次元をPythonとOpenCVで計算するための具体的なアルゴリズムのアイデア。画像（NumPy配列、BGR形式）を入力とし、0.0から1.0の範囲の単一の数値を返す前提で、処理のステップを記述してください。

良い例:
{
    "id": "main_color_saturation",
    "name_ja": "主要色の彩度",
    "description": "画像内で最も支配的な色の彩度の高さ。",
    "algorithm_idea": "1. 画像をBGRからHSV色空間に変換する。 2. S（彩度）チャンネルのヒストグラムを計算する。 3. 最も頻度の高い彩度の値を求め、255で割って正規化する。"
}

上記の要件を厳守し、JSONリストのみを出力してください。
'''

# Lyra軸（感性）生成用のプロンプト
prompt_lyra = '''
あなたは、画像認識システム「SigmaSense」の拡張計画「Lyra」の設計者です。
この計画の目的は、従来の構造的特徴（形状、色）に加え、「感性」的な特徴を捉えることで、特に動物などの複雑で曖昧な対象の認識精度を向上させることです。

これから、動物の画像から「感性」を捉えるための新しい意味次元を設計してください。

要件は以下の通りです。
1.  次元の数は5〜10個程度とします。
2.  各次元は、動物の「らしさ」を捉えるための感性的な特徴を表すものとします。例えば、以下のような概念を参考にしてください。
    -   **揺らぎ度**: 輪郭の揺らぎ、毛並みのフワフワ感など、不定形で柔らかな印象。
    -   **線の柔らかさ**: エッジの強弱、光の回り込みによる境界の曖昧さ。
    -   **動きの余韻**: ブレやモーションブラー、身体のしなやかな流れ。
    -   **視線の印象**: 目や瞳の光、表情から感じられる意図。
3.  各次元は、PythonのOpenCVライブラリやその他の画像統計処理を用いて、具体的なアルゴリズムで計算可能である必要があります。
4.  出力は、JSON形式のリストとしてください。
5.  リストの各要素は、必ず以下のキーを持つJSONオブジェクトでなければなりません。
    - `id`: 次元の一意なID（英語、snake_case）
    - `name_ja`: 日本語の次元名
    - `description`: 次元が何を表すかの簡単な説明
    - `algorithm_idea`: その次元をPythonとOpenCVで計算するための具体的なアルゴリズムのアイデア。画像（NumPy配列、BGR形式）を入力とし、0.0から1.0の範囲の単一の数値を返す前提で、処理のステップを記述してください。

良い例:
{
    "id": "contour_fluctuation",
    "name_ja": "輪郭の揺らぎ",
    "description": "動物の輪郭線の微細な揺らぎや複雑さ。毛並みや不定形な部分を捉える。",
    "algorithm_idea": "1. 画像からCannyエッジを検出する。 2. 検出された最も長い輪郭線を取得する。 3. 輪郭線を構成する点の集合に対して、その凸包を計算する。 4. 輪郭線の実際の長さと、凸包の周囲長の比を計算する。比が大きいほど揺らぎが大きいと判断し、正規化する。"
}

上記の要件を厳守し、JSONリストのみを出力してください。
'''

def generate_dimensions_with_algorithms(prompt, output_filepath):
    """
    Geminiに、指定されたプロンプトに基づき次元定義を生成させる。
    """
    print(f"🚀 Geminiによる次元生成を開始します... (出力先: {output_filepath})")

    try:
        client = GeminiClient()
    except ValueError as e:
        print(f"❗クライアント初期化エラー: {e}")
        return

    print("   - Geminiにプロンプトを送信し、応答を待っています...")
    response_data = client.query_text(prompt)

    if response_data:
        print("   - 応答を受信しました。内容を検証・保存します...")
        
        if isinstance(response_data, str):
            cleaned_response = response_data.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            try:
                parsed_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"❗エラー: Geminiの応答をJSONとして解析できませんでした: {e}")
                print("---" + "-" * 10 + " 受信したデータ " + "-" * 10 + "---")
                print(response_data)
                return
        else:
            parsed_data = response_data

        if isinstance(parsed_data, list) and all('algorithm_idea' in item for item in parsed_data):
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ 新しい次元定義とアルゴリズム案を {output_filepath} に保存しました。")
        else:
            print("❗エラー: Geminiの応答が期待したJSON形式ではありませんでした。リトライしてください。")
            print("---" + "-" * 10 + " 受信したデータ " + "-" * 10 + "---")
            print(parsed_data)

    else:
        print("❗エラー: Geminiから応答がありませんでした。")

def main():
    parser = argparse.ArgumentParser(description="Geminiに意味次元を設計させる、汎用スクリプト")
    parser.add_argument(
        'type',
        nargs='?',
        default=None,
        choices=['selia', 'lyra'],
        help="事前定義済みの次元タイプを選択します ('selia' or 'lyra')。--prompt_fileとは併用できません。"
    )
    parser.add_argument(
        '--prompt_file',
        type=str,
        help="使用するカスタムプロンプトのファイルパス。"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="出力先のJSONファイルパス。--prompt_file使用時は必須です。"
    )
    args = parser.parse_args()

    prompt_to_use = None
    output_filename = None

    if args.prompt_file:
        if args.type:
            print("❗エラー: 'type'引数と '--prompt_file'引数は併用できません。")
            return
        if not args.output:
            print("❗エラー: '--prompt_file' を使用する場合、'--output' で出力ファイル名を指定する必要があります。")
            return
        
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                prompt_to_use = f.read()
            output_filename = args.output
        except FileNotFoundError:
            print(f"❗エラー: プロンプトファイルが見つかりません: {args.prompt_file}")
            return
    
    elif args.type:
        if args.type == 'lyra':
            prompt_to_use = prompt_lyra
            output_filename = "vector_dimensions_custom_ai_lyra.json"
        else: # selia
            prompt_to_use = prompt_selia
            output_filename = "vector_dimensions_custom_ai.json"
    
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    generate_dimensions_with_algorithms(prompt_to_use, output_filename)

if __name__ == "__main__":
    main()
