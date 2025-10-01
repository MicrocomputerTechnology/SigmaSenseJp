import os
import json
from src.hoho.sqlite_knowledge_store import SQLiteStore
from src.hoho.proper_noun_store import ProperNounStore

class WorldModel:
    """
    Acts as a high-level interface to the knowledge stores.
    Manages both the main knowledge graph (concepts, relationships) and a
    specialized store for proper nouns.
    """

    def __init__(self, db_path=None, proper_noun_db_path=None):
        """
        Initializes the WorldModel by creating connections to the knowledge stores.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        if db_path is None:
            db_path = os.path.join(project_root, 'data', 'world_model.sqlite')
        
        if proper_noun_db_path is None:
            proper_noun_db_path = os.path.join(project_root, 'data', 'proper_noun_store.sqlite')

        print(f"WorldModel: Initializing with knowledge store at {db_path}")
        self.store = SQLiteStore(db_path=db_path)

        print(f"WorldModel: Initializing with proper noun store at {proper_noun_db_path}")
        self.proper_noun_store = ProperNounStore(db_path=proper_noun_db_path)

    def add_node(self, node_id, **attributes):
        """Adds or updates a node in the knowledge store."""
        self.store.add_node(node_id, **attributes)

    def add_edge(self, source_id, target_id, relationship, **attributes):
        """Adds or updates a directed edge in the knowledge store."""
        self.store.add_edge(source_id, target_id, relationship, **attributes)

    def get_node(self, node_id):
        """Retrieves node information."""
        return self.store.get_node(node_id)

    def has_node(self, node_id):
        """Checks if a node exists."""
        return self.store.has_node(node_id)

    def find_related_nodes(self, source_id, relationship=None):
        """Finds related nodes connected by a specific relationship."""
        return self.store.find_related_nodes(source_id, relationship)

    # --- Proper Noun Store Methods ---

    def add_proper_noun(self, proper_noun: str, category: str, **attributes):
        """Adds a proper noun and its category to the proper noun store."""
        provenance = attributes.get('provenance', 'inferred')
        self.proper_noun_store.add_proper_noun(proper_noun, category, provenance=provenance)

    def get_category_for_proper_noun(self, proper_noun: str) -> str | None:
        """Gets the category for a given proper noun."""
        return self.proper_noun_store.get_category(proper_noun)

    def get_proper_nouns_by_category(self, category: str) -> list[str]:
        """Gets all proper nouns belonging to a specific category."""
        return self.proper_noun_store.get_proper_nouns_by_category(category)

    def close(self):
        """Closes the connection to all knowledge stores."""
        print("WorldModel: Closing knowledge store connections.")
        if self.store:
            self.store.close()
        if self.proper_noun_store:
            self.proper_noun_store.close()

    # The following methods are now obsolete as persistence is handled by the store.
    def save_graph(self):
        """(Deprecated) Saves the graph. Persistence is now handled by the store."""
        print("WorldModel: save_graph() is deprecated. The SQLite store saves automatically.")
        # The store's save is now commit, which is called after each transaction.
        # This method can be a no-op or call save for legacy compatibility.
        pass

    def load_graph(self):
        """(Deprecated) Loads the graph. This is now handled by the store's constructor."""
        print("WorldModel: load_graph() is deprecated.")
        pass
