from abc import ABC, abstractmethod

class KnowledgeStoreBase(ABC):
    """Abstract base class for a knowledge store, defining the interface."""

    @abstractmethod
    def add_node(self, node_id: str, **attributes):
        """Adds a node to the knowledge store."""
        pass

    @abstractmethod
    def get_node(self, node_id: str):
        """Retrieves a node from the knowledge store."""
        pass

    @abstractmethod
    def has_node(self, node_id: str) -> bool:
        """Checks if a node exists in the knowledge store."""
        pass

    @abstractmethod
    def add_edge(self, source_id: str, target_id: str, relationship: str, **attributes):
        """Adds a directed edge to the knowledge store."""
        pass

    @abstractmethod
    def find_related_nodes(self, source_id: str, relationship: str = None):
        """Finds nodes connected from a given source node."""
        pass

    @abstractmethod
    def close(self):
        """Closes any open connections to the store."""
        pass

    @abstractmethod
    def save(self):
        """For file-based stores, saves the current state."""
        pass
