import os
import json
from .sqlite_knowledge_store import SQLiteStore

class WorldModel:
    """
    Acts as a high-level interface to the knowledge store.
    Decouples the rest of the system from the specific storage implementation (e.g., JSON, SQLite, Neo4j).
    """

    def __init__(self, db_path=None):
        """
        Initializes the WorldModel by creating a connection to the knowledge store.
        """
        if db_path is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(project_root, 'data', 'world_model.sqlite')
        
        print(f"WorldModel: Initializing with knowledge store at {db_path}")
        self.store = SQLiteStore(db_path=db_path)

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

    def close(self):
        """Closes the connection to the knowledge store."""
        print("WorldModel: Closing knowledge store connection.")
        self.store.close()

    # The following methods are now obsolete as persistence is handled by the store.
    def save_graph(self):
        """(Deprecated) Saves the graph. Persistence is now handled by the store."""
        print("WorldModel: save_graph() is deprecated. The SQLite store saves automatically.")
        self.store.save() # Call the store's save method for consistency

    def load_graph(self):
        """(Deprecated) Loads the graph. This is now handled by the store's constructor."""
        print("WorldModel: load_graph() is deprecated.")
        pass
