from src.hoho.knowledge_store_base import KnowledgeStoreBase

class NebulaGraphStore(KnowledgeStoreBase):
    def __init__(self, host: str, port: int, space: str):
        pass

    def add_node(self, node_id: str, **attributes):
        pass

    def add_edge(self, source_id: str, target_id: str, relationship: str, **attributes):
        pass

    def get_node(self, node_id: str):
        pass

    def find_related_nodes(self, source_id: str, relationship: str = None):
        pass

    def add_memory(self, memory_data: dict):
        pass

    def get_all_memories(self):
        pass
