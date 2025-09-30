import pytest
import os
from src.proper_noun_store import ProperNounStore

@pytest.fixture
def db_path():
    # Use an in-memory SQLite database for tests
    return ":memory:"

@pytest.fixture
def store(db_path):
    # Create a store instance for each test
    store = ProperNounStore(db_path)
    yield store
    store.close()

def test_initialization(store):
    """Test that the database and tables are created on initialization."""
    cursor = store.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='proper_nouns'")
    assert cursor.fetchone() is not None, "The 'proper_nouns' table should be created."

def test_add_and_get_proper_noun(store):
    """Test adding a new proper noun and retrieving its category."""
    store.add_proper_noun("東京", "都市")
    category = store.get_category("東京")
    assert category == "都市"

def test_get_non_existent_noun(store):
    """Test retrieving a category for a noun that doesn't exist."""
    category = store.get_category("大阪")
    assert category is None

def test_add_duplicate_updates_category(store):
    """Test that adding a noun with an existing key updates the category."""
    store.add_proper_noun("富士山", "山")
    store.add_proper_noun("富士山", "火山") # Update category
    category = store.get_category("富士山")
    assert category == "火山"

def test_get_proper_nouns_by_category(store):
    """Test retrieving all proper nouns associated with a specific category."""
    store.add_proper_noun("東京", "都市")
    store.add_proper_noun("大阪", "都市")
    store.add_proper_noun("エベレスト", "山")

    cities = store.get_proper_nouns_by_category("都市")
    mountains = store.get_proper_nouns_by_category("山")
    empty_category = store.get_proper_nouns_by_category("川")

    assert sorted(cities) == ["大阪", "東京"]
    assert mountains == ["エベレスト"]
    assert empty_category == []

def test_provenance_and_last_updated(store):
    """Test that provenance and last_updated fields are handled correctly."""
    store.add_proper_noun("アインシュタイン", "科学者", provenance="manual")
    
    cursor = store.connection.cursor()
    cursor.execute("SELECT provenance, last_updated FROM proper_nouns WHERE proper_noun = ?", ("アインシュタイン",))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == "manual"
    assert row[1] is not None # Check that last_updated is set

    # Test default provenance
    store.add_proper_noun("ニュートン", "科学者")
    cursor.execute("SELECT provenance FROM proper_nouns WHERE proper_noun = ?", ("ニュートン",))
    row = cursor.fetchone()
    assert row[0] == "inferred"
