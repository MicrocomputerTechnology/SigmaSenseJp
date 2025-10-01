# 設定ファイル

このディレクトリには、SigmaSenseエージェントの振る舞いや知識ベースを定義する設定ファイルが含まれています。

## 主要な設定

- **`sigma_sense_config.json`**: SigmaSenseシステムのメイン設定ファイルです。
- **`octasense_config.yaml`**: 第十六次世代の倫理フレームワークである「Octasense」システムの設定です。

## 意味次元定義

これらのファイルは、システムが世界を理解するために使用する「ものさし」、すなわち意味次元を定義します。これらはニューロシンボリック・アーキテクチャの中核をなす部分です。

- **`vector_dimensions_mobile.yaml` / `vector_dimensions_mobile_optimized.yaml`**: モバイルやリソースに制約のある環境向けに最適化された次元です。
- **`vector_dimensions_custom_ai.json` / `_lyra.json` / `_terrier.json`**: AI（「オリエン大賢者」）によって設計された次元です。異なるファイルは、異なるレイヤーや特化したタスク（例：`lyra`は複雑・生物学的形状、`terrier`は特定の犬種）に対応しています。
- **`vector_dimensions_test_logic.json`**: 論理的推論をテストするために特化した次元です。

## エージェントとモデルのプロファイル

これらのファイルは、SigmaSense内の様々なAIエージェントやモデルのミッション、振る舞い、プロファイルを定義します。

- **`saphiel_mission_profile.json`**: 意味軸の設計を担当するエージェント「サフィール」のミッションプロファイルです。
- **`sigma_local_core_profile.json`**: オフラインの中核知性「ヴェトラ」のプロファイルです。
- **`vetra_llm_core_profile.json`**: ヴェトラが使用するLLMのプロファイルです。
- **`toyokawa_model_profile.json`**: システム全体の集合的な心理状態を観測する「豊川モデル」のプロファイルです。
- **倫理フレームワークプロファイル**: `ethical_filter_profile.json`、`contextual_compassion_profile.json`など、「八人の誓い」の倫理フレームワークのための一連のプロファイルです。

## 知識とデータベース

- **`sigma_product_database_stabilized.json`**: 既知のオブジェクトに対する、安定化された意味ベクトルのメインデータベースです。
- **`world_model.json`**: システムの「常識」を表す動的知識グラフです。概念とそれらの関係を含み、時間とともに学習・更新されます。
- **`common_sense_rulebase.json`**: `SymbolicReasoner`が、動的な`world_model.json`が完全に実装される前に使用していたと思われる、静的な常識のルールブックです。