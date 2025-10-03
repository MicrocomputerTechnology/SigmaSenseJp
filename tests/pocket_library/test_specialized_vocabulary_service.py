
import pytest
from src.pocket_library.specialized_vocabulary_service import SpecializedVocabularyService

@pytest.fixture
def service():
    """Provides a SpecializedVocabularyService instance."""
    s = SpecializedVocabularyService()
    yield s
    s.close()

def test_service_initialization(service: SpecializedVocabularyService):
    """Tests if the main service initializes."""
    assert service is not None

def test_python_vocab_handler_initialization(service: SpecializedVocabularyService):
    """Tests if the Python vocabulary handler is initialized."""
    assert service.python_vocab_handler is not None
    assert service.python_vocab_handler.connection is not None

def test_philosophy_vocab_handler_initialization(service: SpecializedVocabularyService):
    """Tests if the philosophy vocabulary handler is initialized."""
    assert service.philosophy_vocab_handler is not None
    assert service.philosophy_vocab_handler.connection is not None

def test_get_math_definition(service: SpecializedVocabularyService):
    """Tests the SymPy integration."""
    result = service.get_math_definition("pi")
    assert "error" not in result
    assert result["value"].startswith("3.14")
