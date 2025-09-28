## 5. 関手性に基づく自己修正ワークフロー

理論的な保証だけでなく、SigmaSenseは圏論の理念を実用的な品質保証サイクルとして実装しています。システムの論理的整合性、特に**関手性**は、開発の過程で常に検証され、維持されなければなりません。そのために、以下の半自動的な「診断・治療」ワークフローが用意されています。

このワークフローは、システムの振る舞いに予期せぬ「副作用」（例：画像を回転させたら、形だけでなく色まで変わってしまう）が発生していないかを検出し、それを自動的に補正することで、意味データベースの品質を継続的に向上させることを目的とします。

### ワークフローの登場人物

1.  **診断医 (`tools/functor_consistency_checker.py`)**:
    `SigmaFunctor`モジュールを利用し、テスト画像に様々な変換（回転、色調変更など）を加えます。その際、単に副作用がないかを確認するだけでなく、画像への変換がベクトル空間上で期待通りの変換を引き起こすかという「関手性」そのものを検証し、システムの論理的な一貫性が構造的に保たれているかを精密に検査します。

2.  **カルテ (`functor_consistency_failures.jsonl`)**:
    「診断医」が発見した全ての問題点が、このログファイルに詳細に記録されます。どの画像に、どの変換を施した際に、どの次元が、どれくらい予期せぬ変化をしたのかが、後の修正プロセスで利用できる形式で保存されます。

3.  **治療薬 (`stabilize_database.py`)**:
    「カルテ」に記録された問題点を読み込み、データベース全体に対して自動的な補正処理を行います。予期せぬ影響を受けてしまったベクトルの次元を、その影響を打ち消す方向に修正し、より安定的で論理的に一貫した新しいデータベース (`sigma_product_database_stabilized.json`) を生成します。

### 実行ステップ

このワークフローは、以下の手動ステップを通じて実行されます。

**事前にLLMのモデルを用意する必要があります。**

models  
├── efficientnet_lite0.tflite  
├── mobilenet_v1.tflite  
├── mobilevit-tensorflow2-xxs-1k-256-v1  
│   ├── keras_metadata.pb  
│   ├── saved_model.pb  
│   └── variables  
│       ├── variables.data-00000-of-00001  
│       └── variables.index  
└── resnet_v2_50_saved_model  
.   ├── saved_model.pb  
.   └── variables  
.        ├── variables.data-00000-of-00001  
.        └── variables.index  

1.  **Step 1: 診断の実行**:
    開発者は `python tools/functor_consistency_checker.py` を実行し、現在のデータベースとベクトル生成ロジックの健康状態を診断します。問題があれば `functor_consistency_failures.jsonl` が生成・更新されます。

2.  **Step 2: 治療の実行**:
    次に `python src/stabilize_database.py` を実行します。このスクリプトは診断結果（カルテ）を元に、元のデータベースを補正し、安定化させた新しいデータベースを生成します。デフォルトでは、`config/sigma_product_database_custom_ai_generated.json` を読み込み、`config/sigma_product_database_stabilized.json` を生成します。入力元と出力先は `--source` と `--output` 引数で変更可能です。

3.  **Step 3: 再診断**:
    安定化されたデータベースを用いて、再度 `tools/functor_consistency_checker.py` を実行し、問題が解消されたかを確認します。

この「診断 → 治療 → 再診断」のサイクルを繰り返すことで、SigmaSenseの意味データベースは、その論理的整合性を常に高く維持し、信頼性の高い照合性能を実現しています。

  > **Note**
  > `dimension_loader`やベクトル生成エンジンなど、システムの根幹に関わる変更を行った後は、古い`functor_consistency_failures.jsonl`が原因で`build_database.py`が失敗することがあります。その場合は、このファイルを削除してから、再度ワークフローを実行してください。