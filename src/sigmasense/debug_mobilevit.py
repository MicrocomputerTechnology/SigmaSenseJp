
print("--- MobileViTエンジン単体でのデバッグテストを開始します ---")

try:
    # MobileViTエンジンクラスをインポート
    from sigma_image_engines.engine_mobilevit import MobileViTEngine
    print("エンジンのインポートに成功しました。初期化を開始します...")
    
    # エンジンを初期化
    engine = MobileViTEngine()
    
    # モデルが正常にロードされたかを確認
    if engine.model:
        print("\n[成功] エンジンの初期化が正常に完了しました。")
        print("MobileViTのSavedModelは、単体で問題なく動作するようです。")
    else:
        print("\n[失敗] エンジンの初期化に失敗しました。")
        print("以前のログに表示されたエラーメッセージを確認してください。")

except Exception as e:
    print(f"\n[エラー] インポートまたは初期化の際に、予期せぬエラーが発生しました: {e}")

print("--- デバッグテストを終了します ---")
