import json
import os
import time
from PIL import Image
from gemini_client import GeminiClient

def load_dimensions(filepath="vector_dimensions_custom_ai.json"):
    """次元定義ファイル(JSON)を読み込む"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❗エラー: 次元定義ファイルが見つかりません: {filepath}")
        return None

def generate_vector_for_image(client, image_path, dimensions):
    """
    単一の画像と次元定義をGeminiに渡し、画像ベクトルを生成させる。
    """
    dimensions_text = "\n".join([
        f"- {dim['id']} ({dim.get('name_ja', dim['id'])}): {dim['description']}" 
        for dim in dimensions
    ])

    prompt = f"""
    あなたは画像分析AI「SigmaSense」です。
    あなたのタスクは、与えられた画像を分析し、以下の意味次元定義に基づいて、それをベクトル表現に変換することです。

    --- 意味次元定義 ---
    {dimensions_text}
    --------------------------

    上の定義に従い、添付された画像を分析してください。
    各次元に対して、画像がその特性をどの程度持っているかを0.0から1.0の範囲で評価し、
    全次元の評価値を一つのJSONオブジェクトとして出力してください。
    キーは次元のid、値は評価スコアとします。

    例: {{'circularity': 0.8, 'complexity': 0.5, ...}}

    説明や言い訳は不要で、JSONブロックのみを返してください。
    """

    try:
        img = Image.open(image_path)
        response_data = client.query_multimodal([prompt, img])
        
        if response_data:
            if all(dim['id'] in response_data for dim in dimensions):
                return response_data
            else:
                print("❗レスポンスに必要な次元IDが不足しています。")
                return None
        return None

    except FileNotFoundError:
        print(f"❗画像ファイルが見つかりません: {image_path}")
        return None
    except Exception as e:
        print(f"❗画像ベクトル生成中にエラー: {e}")
        return None

def main():
    """
    メイン処理: 全画像に対してAIにベクトル生成を依頼し、データベースを構築する。
    """
    print("🚀 Geminiによる画像ベクトルデータベースの構築を開始します。")
    
    dimensions = load_dimensions()
    if not dimensions:
        return

    try:
        client = GeminiClient()
    except ValueError as e:
        print(f"❗クライアント初期化エラー: {e}")
        return

    image_dir = "sigma_images"
    image_files = [f for f in sorted(os.listdir(image_dir)) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    database_entries = []

    print(f"\n全{len(image_files)}個の画像について、ベクトル生成を行います...")
    for i, fname in enumerate(image_files):
        image_path = os.path.join(image_dir, fname)
        print(f" [{i+1}/{len(image_files)}] '{fname}' を処理中...")
        
        time.sleep(1) # APIのレート制限を考慮
        
        vector_map = generate_vector_for_image(client, image_path, dimensions)
        
        if vector_map:
            ordered_vector = [vector_map.get(dim['id'], 0.0) for dim in dimensions]
            
            # 拡張子を除いたファイル名をIDとする
            image_id = os.path.splitext(fname)[0]

            database_entries.append({
                "id": image_id,
                "meaning_vector": ordered_vector
            })
            print(f"   -> 生成成功")
        else:
            print(f"   -> 生成失敗")

    output_filename = "sigma_product_database_custom_ai_generated.json"
    print(f"\n✅ 全画像のベクトル生成が完了しました。")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(database_entries, f, indent=2, ensure_ascii=False)
    
    print(f"結果を {output_filename} に保存しました。")

if __name__ == "__main__":
    main()

