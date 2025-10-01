# Sigma画像エンジン

このディレクトリには、`DimensionGenerator`が画像から特徴を抽出するために使用するさまざまなエンジンが含まれています。各エンジンは入力画像に対して異なる視点を提供し、それらの出力を組み合わせて包括的な意味ベクトルが作成されます。

このマルチエンジンアーキテクチャは、SigmaSenseが堅牢で多面的な分析を実行する能力の重要な部分です。

## エンジン

- **`engine_opencv.py` / `engine_opencv_legacy.py`**: OpenCVライブラリの伝統的なコンピュータビジョン技術を使用して特徴を抽出します。これらには、形状記述子（Huモーメントなど）、カラーヒストグラム、テクスチャ分析などが含まれる可能性があります。

- **`engine_efficientnet.py`**: 軽量で強力な畳み込みニューラルネットワーク（CNN）であるEfficientNetモデルを使用して、高レベルのセマンティックな特徴を抽出します。

- **`engine_mobilenet.py`**: モバイルおよび組み込みデバイス向けに設計された別の軽量CNNであるMobileNetモデルを使用します。

- **`engine_mobilevit.py`**: CNNとVision Transformerの長所を組み合わせて画像内の局所的および大域的な特徴を捉えるMobileViTモデルを使用します。

- **`engine_resnet.py`**: 古典的で強力なCNNアーキテクチャであるResNet（Residual Network）モデルを使用します。