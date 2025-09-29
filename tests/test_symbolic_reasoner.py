import unittest
import os
import json
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.world_model import WorldModel
from src.symbolic_reasoner import SymbolicReasoner

class TestSymbolicReasoner(unittest.TestCase):

    def setUp(self):
        """テストごとに、一時的なSQLiteデータベースを持つWorldModelを構築"""
        self.test_db_path = 'test_reasoner_wm.sqlite'
        # 古いテストファイルが残っていれば削除
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        # WorldModelは内部でSQLiteStoreを初期化する
        self.wm = WorldModel(db_path=self.test_db_path)
        
        # テストデータをプログラムで追加
        self.wm.add_node('penguin', name_ja="ペンギン")
        self.wm.add_node('bird', name_ja="鳥")
        self.wm.add_node('animal', name_ja="動物")
        self.wm.add_edge('penguin', 'bird', 'is_a')
        self.wm.add_edge('bird', 'animal', 'is_a')

        self.wm.add_node('団子', name_ja="団子")
        self.wm.add_node('和菓子', name_ja="和菓子")
        self.wm.add_node('食べ物', name_ja="食べ物")
        self.wm.add_node('重し', name_ja="重し")
        self.wm.add_node('物体', name_ja="物体")
        self.wm.add_edge('団子', '和菓子', 'is_a')
        self.wm.add_edge('和菓子', '食べ物', 'is_a')
        self.wm.add_edge('重し', '物体', 'is_a')

        self.reasoner = SymbolicReasoner(world_model=self.wm)

    def tearDown(self):
        """テスト後に一時的なデータベースファイルを削除"""
        self.wm.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_get_all_supertypes(self):
        """get_all_supertypesが正しく上位概念を再帰的に取得できるかテスト"""
        dango_supertypes = self.reasoner.get_all_supertypes('団子')
        expected_supertypes = {'和菓子', '食べ物'}
        self.assertEqual(dango_supertypes, expected_supertypes)
        print("\nget_all_supertypes test passed.")

    def test_check_category_consistency(self):
        """check_category_consistencyが論理的矛盾を正しく検出できるかテスト"""
        # 矛盾がないケース
        consistent_result = self.reasoner.check_category_consistency(['団子'])
        self.assertTrue(consistent_result['consistent'])

        # 矛盾があるケース
        inconsistent_result = self.reasoner.check_category_consistency(['団子', '重し'])
        expected_inconsistency = {
            'consistent': False,
            'reason': "In a '食べ物' context, item '重し' is not a 食べ物.",
            'violator': '重し',
            'context_category': '食べ物'
        }
        self.assertEqual(inconsistent_result, expected_inconsistency)
        print("Inconsistency detection test ('団子' vs '重し') passed.")

if __name__ == '__main__':
    unittest.main()
