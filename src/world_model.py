# === 第十五次実験 実装ファイル ===

from .config_loader import ConfigLoader

class WorldModel:
    """
    動的知識グラフ（ワールドモデル）を管理するクラス。

    目的：
    - 「鳥は飛ぶ」といった一般的な知識や、「ペンギンは飛べない鳥である」といった例外ルール、
      さらには実験を通じて学習した新しい因果関係を、単一のグラフ構造として動的に管理する。
    """

    def __init__(self, config: dict = None):
        """
        WorldModelを初期化する。
        指定されたパスにグラフファイルが存在すれば読み込み、なければ新しいグラフを作成する。

        Args:
            config (dict): 設定オブジェクト。
        """
        if config is None:
            config = {}

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        default_graph_path = os.path.join(project_root, 'config', "world_model.json")

        graph_path_from_config = config.get("graph_path")
        
        if graph_path_from_config:
            # If the path from config is not absolute, join it with the project root
            if not os.path.isabs(graph_path_from_config):
                self.graph_path = os.path.join(project_root, graph_path_from_config)
            else:
                self.graph_path = graph_path_from_config
        else:
            self.graph_path = default_graph_path
            
        self.graph = {
            "nodes": {},
            "edges": []
        }
        if os.path.exists(self.graph_path):
            self.load_graph()

    def load_graph(self):
        """グラフをJSONファイルから読み込む。"""
        try:
            with open(self.graph_path, 'r', encoding='utf-8') as f:
                self.graph = json.load(f)
            print(f"WorldModel: Loaded graph from {self.graph_path}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"WorldModel: Error loading graph from {self.graph_path}. Starting with an empty graph. Error: {e}")
            self.graph = {"nodes": {}, "edges": []} # 読み込み失敗時は空のグラフで初期化

    def save_graph(self):
        """現在のグラフをJSONファイルに保存する。"""
        try:
            os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
            with open(self.graph_path, 'w', encoding='utf-8') as f:
                json.dump(self.graph, f, indent=4, ensure_ascii=False)
            print(f"WorldModel: Graph saved to {self.graph_path}")
        except IOError as e:
            print(f"WorldModel: Error saving graph to {self.graph_path}. Error: {e}")

    def add_node(self, node_id, **attributes):
        """
        グラフにノードを追加または更新する。

        Args:
            node_id (str): ノードの一意なID。
            **attributes: ノードに付随する属性（例: name="鳥", type="concept"）。
        """
        if node_id not in self.graph["nodes"]:
            self.graph["nodes"][node_id] = {"id": node_id}
        self.graph["nodes"][node_id].update(attributes)
        print(f"WorldModel: Added/Updated node '{node_id}'")

    def add_edge(self, source_id, target_id, relationship, **attributes):
        """
        グラフに有向エッジを追加する。

        Args:
            source_id (str): エッジの始点ノードID。
            target_id (str): エッジの終点ノードID。
            relationship (str): エッジが表す関係性（例: "is_a", "has_property"）。
            **attributes: エッジに付随する属性（例: weight=0.9, provenance="Experiment_14"）。
        """
        if source_id not in self.graph["nodes"] or target_id not in self.graph["nodes"]:
            print(f"WorldModel: Error adding edge. Source or target node does not exist.")
            return

        # 重複を避けるため、同じ始点・終点・関係性のエッジが既に存在するかチェック
        edge_exists = False
        for edge in self.graph["edges"]:
            if edge["source"] == source_id and edge["target"] == target_id and edge["relationship"] == relationship:
                edge.update(attributes)
                edge_exists = True
                break
        
        if not edge_exists:
            new_edge = {
                "source": source_id,
                "target": target_id,
                "relationship": relationship
            }
            new_edge.update(attributes)
            self.graph["edges"].append(new_edge)
        
        print(f"WorldModel: Added/Updated edge: {source_id} -[{relationship}]-> {target_id}")

    def get_node(self, node_id):
        """
        指定されたIDのノード情報を取得する。

        Args:
            node_id (str): 取得するノードのID。

        Returns:
            dict or None: ノードの情報。存在しない場合はNone。
        """
        return self.graph["nodes"].get(node_id)

    def has_node(self, node_id):
        """
        指定されたIDのノードがグラフに存在するかを確認する。

        Args:
            node_id (str): 確認するノードのID。

        Returns:
            bool: ノードが存在すればTrue、しなければFalse。
        """
        return node_id in self.graph["nodes"]

    def get_all_node_ids(self):
        """
        グラフに存在するすべてのノードIDのリストを返す。

        Returns:
            list: すべてのノードIDのリスト。
        """
        return list(self.graph["nodes"].keys())

    def find_related_nodes(self, source_id, relationship=None):
        """
        指定されたノードから特定の種類の関係性で繋がるノードを検索する。

        Args:
            source_id (str): 始点となるノードのID。
            relationship (str, optional): 検索する関係性の種類。Noneの場合は全てのエッジを対象とする。

        Returns:
            list: 関連するノードの情報とエッジの属性を含む辞書のリスト。
        """
        related = []
        for edge in self.graph["edges"]:
            if edge["source"] == source_id:
                if relationship is None or edge["relationship"] == relationship:
                    related.append({
                        "target_node": self.get_node(edge["target"]),
                        "edge_attributes": {k: v for k, v in edge.items() if k not in ['source', 'target']}
                    })
        return related

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    import tempfile

    print("--- WorldModel Self-Test --- ")
    # テスト用に安全な一時ファイルを作成
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w')
    test_graph_path = tmpfile.name
    tmpfile.close() # ファイル名を確保するために一度閉じる

    test_config = {"graph_path": test_graph_path}

    try:
        # 1. モデルの初期化
        wm = WorldModel(config=test_config)

        # 2. ノードの追加
        wm.add_node('bird', name_ja="鳥", type="concept")
        wm.add_node('penguin', name_ja="ペンギン", type="instance")
        wm.add_node('can_fly', name_ja="飛べる", type="property")
        wm.add_node('cannot_fly', name_ja="飛べない", type="property")

        # 3. エッジの追加
        wm.add_edge('penguin', 'bird', 'is_a', provenance="Initial Knowledge")
        wm.add_edge('bird', 'can_fly', 'has_property', confidence=0.9)
        wm.add_edge('penguin', 'cannot_fly', 'has_property', confidence=1.0, note="This is an exception.")

        # 4. グラフの保存
        wm.save_graph()

        # 5. グラフの検索
        print("\n--- Querying Graph ---")
        penguin_node = wm.get_node('penguin')
        print(f"Penguin Node: {penguin_node}")

        bird_properties = wm.find_related_nodes('bird', relationship='has_property')
        print(f"Properties of Bird: {bird_properties}")

        penguin_relations = wm.find_related_nodes('penguin')
        print(f"All relations from Penguin: {penguin_relations}")

        # 6. 新しいモデルインスタンスで読み込みテスト
        print("\n--- Testing Persistence ---")
        wm_new = WorldModel(config=test_config)
        penguin_node_new = wm_new.get_node('penguin')
        print(f"Penguin Node from new instance: {penguin_node_new}")
        assert penguin_node == penguin_node_new
        print("Persistence test passed.")

    finally:
        # クリーンアップ
        if os.path.exists(test_graph_path):
            os.remove(test_graph_path)
        print("\n--- Self-Test Complete ---")