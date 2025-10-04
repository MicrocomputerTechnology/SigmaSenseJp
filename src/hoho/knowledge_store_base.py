from abc import ABC, abstractmethod
from typing import Optional

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
    def find_related_nodes(self, source_id: str, relationship: Optional[str] = None):
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

    @abstractmethod
    def add_memory(self, memory_data: dict):
        """Adds a personal memory record to the store."""
        pass

    @abstractmethod
    def get_all_memories(self) -> list:
        """Retrieves all personal memory records from the store."""
        pass

    @abstractmethod
    def add_vector(self, vector_id: str, vector: list, layer: str):
        """Adds a vector to the vector database."""
        pass

    @abstractmethod
    def get_all_vectors(self) -> tuple[list, list, list]:
        """Retrieves all records from the vector database."""
        pass

    @abstractmethod
    def clear_vector_database(self):
        """Clears all records from the vector database."""
        pass
