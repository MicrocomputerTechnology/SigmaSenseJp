
import pytest
from src.pocket_library.dictionary_service import DictionaryService

@pytest.fixture
def service():
    """Provides a DictionaryService instance."""
    s = DictionaryService()
    yield s
    s.close() # Clean up database connection

def test_service_initialization(service: DictionaryService):
    """Tests if the main service initializes."""
    assert service is not None

def test_sudachi_tokenizer_initialization(service: DictionaryService):
    """Tests if the Sudachi tokenizer is initialized."""
    assert service.sudachi_tokenizer is not None

def test_mecab_tokenizer_initialization(service: DictionaryService):
    """Tests if the MeCab tokenizer is initialized."""
    assert service.mecab_tokenizer is not None

def test_ejdict_handler_initialization(service: DictionaryService):
    """Tests if the EJDict handler is initialized and connected."""
    assert service.ejdict_handler is not None
    assert service.ejdict_handler.connection is not None
