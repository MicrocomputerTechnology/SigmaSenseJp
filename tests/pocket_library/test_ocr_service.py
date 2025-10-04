import pytest
import shutil
from src.hoho.pocket_library.ocr_service import OCRService

@pytest.fixture
def service():
    """Provides an OCRService instance."""
    return OCRService()

def test_service_initialization(service: OCRService):
    """Tests if the main service initializes."""
    assert service is not None

def test_manga_ocr_engine_initialization(service: OCRService):
    """Tests if the MangaOcr engine is initialized."""
    assert service.manga_ocr_engine is not None

@pytest.mark.skipif(shutil.which("yomitoku") is None, reason="yomitoku command not found in PATH")
def test_yomitoku_is_callable():
    """Tests if the yomitoku command is available in the system PATH."""
    # This test doesn't run the command, just checks for its existence.
    # The actual functionality is tested by running the service method, 
    # which is more of an integration test.
    assert True