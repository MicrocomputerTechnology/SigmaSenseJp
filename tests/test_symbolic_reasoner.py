import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import pytest

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.world_model import WorldModel
from src.symbolic_reasoner import SymbolicReasoner, _normalize_str

# GiNZAが利用可能かチェック
try:
    import spacy
    spacy.load("ja_ginza")
    ginza_available = True
except (OSError, ImportError):
    ginza_available = False

class TestSymbolicReasoner(unittest.TestCase):

    def setUp(self):
        """テストごとに、一時的なデータベースを持つWorldModelを構築"""
        self.test_db_path = os.path.abspath('test_wm.sqlite')
        self.proper_noun_db_path = os.path.abspath('test_pn.sqlite')
        
        for path in [self.test_db_path, self.proper_noun_db_path]:
            if os.path.exists(path):
                os.remove(path)

        self.wm = WorldModel(db_path=self.test_db_path, proper_noun_db_path=self.proper_noun_db_path)
        
        # 一般的な概念のテストデータを追加
        self.wm.add_node('penguin', name_ja="ペンギン")
        self.wm.add_node('bird', name_ja="鳥")
        self.wm.add_node('animal', name_ja="動物")
        self.wm.add_edge('penguin', 'bird', 'is_a')
        self.wm.add_edge('bird', 'animal', 'is_a')

        self.wm.add_node('都市', name_ja="都市")
        self.wm.add_node('場所', name_ja="場所")
        self.wm.add_edge('都市', '場所', 'is_a')
        
        self.wm.add_node('食べ物', name_ja="食べ物")

        # 既知の固有名詞をストアに追加
        self.wm.add_proper_noun("仙台", "都市")

        self.reasoner = SymbolicReasoner(world_model=self.wm)

    def tearDown(self):
        """テスト後に一時的なデータベースファイルを削除"""
        self.wm.close()
        self.reasoner.dictionary_service.close()
        for path in [self.test_db_path, self.proper_noun_db_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_get_supertypes_for_common_noun(self):
        """既知の一般名詞の上位概念が正しく取得できるかテスト"""
        supertypes = self.reasoner.get_all_supertypes('penguin')
        self.assertEqual(supertypes, {'bird', 'animal'})

    def test_get_supertypes_for_known_proper_noun(self):
        """既知の固有名詞の上位概念が正しく取得できるかテスト"""
        supertypes = self.reasoner.get_all_supertypes('仙台')
        self.assertEqual(supertypes, {'都市', '場所'})

    @unittest.skipUnless(ginza_available, "GiNZA is not installed, skipping NER-dependent test")
    def test_unknown_proper_noun_calls_dictionary_service(self):
        """未知の固有名詞の場合にDictionaryServiceが呼ばれるかテスト"""
        with patch.object(self.reasoner, '_is_proper_noun', return_value=(True, 'GPE')) as mock_is_proper:
            with patch.object(self.reasoner.dictionary_service, 'tokenize_japanese_text_sudachi', return_value=[]) as mock_sudachi:
                with patch.object(self.reasoner.dictionary_service, 'get_supertypes_from_wordnet', return_value=set()) as mock_wordnet:
                    self.reasoner.get_all_supertypes('沖縄')
                    mock_is_proper.assert_called_once_with('沖縄')
                    mock_sudachi.assert_called_once()
                    mock_wordnet.assert_called_once()

    def test_unknown_common_noun_calls_dictionary_service(self):
        """未知の一般名詞の場合にDictionaryServiceが呼ばれるかテスト"""
        with patch.object(self.reasoner, '_is_proper_noun', return_value=(False, None)) as mock_is_proper:
            with patch.object(self.reasoner.dictionary_service, 'tokenize_japanese_text_sudachi', return_value=[]) as mock_sudachi:
                with patch.object(self.reasoner.dictionary_service, 'get_supertypes_from_wordnet', return_value=set()) as mock_wordnet:
                    self.reasoner.get_all_supertypes('コンピューター')
                    mock_is_proper.assert_called_once_with('コンピューター')
                    mock_sudachi.assert_called_once()
                    mock_wordnet.assert_called_once()

    def test_reason_with_mixed_context(self):
        """固有名詞と一般名詞が混在したコンテキストでreasonが正しく動作するかテスト"""
        context = {'仙台': True, 'penguin': True}
        inferred = self.reasoner.reason(context)
        self.assertEqual(inferred, {'都市': True, '場所': True, 'bird': True, 'animal': True})

if __name__ == '__main__':
    unittest.main()