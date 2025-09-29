import sqlite3
import json
import os
from datetime import datetime, UTC
from .knowledge_store_base import KnowledgeStoreBase

class SQLiteStore(KnowledgeStoreBase):
    """SQLite-backed implementation of the KnowledgeStore."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure the directory for the db exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.connection.cursor()
        # Node table with swarm-aware columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                domain TEXT,
                attributes TEXT, -- JSON blob for other attributes
                provenance TEXT,
                last_updated TEXT
            )
        ''')
        # Edge table with swarm-aware columns and uniqueness constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                source_id TEXT,
                target_id TEXT,
                relationship TEXT,
                weight REAL DEFAULT 1.0,
                confidence REAL DEFAULT 1.0,
                provenance TEXT,
                last_updated TEXT,
                PRIMARY KEY (source_id, target_id, relationship)
            )
        ''')
        # Personal Memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT UNIQUE,
                timestamp TEXT,
                source_image_name TEXT,
                vector TEXT,
                best_match_id TEXT,
                best_match_score REAL,
                logical_terms TEXT,
                psyche_state TEXT,
                self_correlation_score REAL
            )
        ''')

        # Indexes for fast traversal
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON edges (source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON edges (target_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_relationship ON edges (relationship)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON personal_memory (timestamp)')

        # Vector Database table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_database (
                id TEXT PRIMARY KEY,
                vector TEXT,
                layer TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vector_layer ON vector_database (layer)')

        self.connection.commit()

    def add_node(self, node_id: str, **attributes):
        cursor = self.connection.cursor()
        domain = attributes.pop('domain', None)
        provenance = attributes.pop('provenance', 'manual')
        last_updated = datetime.now(UTC).isoformat()
        attributes_json = json.dumps(attributes)
        cursor.execute('''
            INSERT OR REPLACE INTO nodes (id, domain, attributes, provenance, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (node_id, domain, attributes_json, provenance, last_updated))
        self.connection.commit()

    def get_node(self, node_id: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT attributes FROM nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def has_node(self, node_id: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM nodes WHERE id = ?", (node_id,))
        return cursor.fetchone() is not None

    def add_edge(self, source_id: str, target_id: str, relationship: str, **attributes):
        cursor = self.connection.cursor()
        weight = attributes.get('weight', 1.0)
        confidence = attributes.get('confidence', 1.0)
        provenance = attributes.get('provenance', 'manual')
        last_updated = datetime.now(UTC).isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO edges (source_id, target_id, relationship, weight, confidence, provenance, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (source_id, target_id, relationship, weight, confidence, provenance, last_updated))
        self.connection.commit()

    def find_related_nodes(self, source_id: str, relationship: str = None):
        cursor = self.connection.cursor()
        query = """
            SELECT e.target_id, n.attributes, e.relationship, e.weight, e.confidence, e.provenance
            FROM edges e JOIN nodes n ON e.target_id = n.id
            WHERE e.source_id = ?
        """
        params = [source_id]
        if relationship:
            query += " AND e.relationship = ?"
            params.append(relationship)
        
        cursor.execute(query, params)
        
        related = []
        for row in cursor.fetchall():
            target_node_attributes = json.loads(row[1])
            target_node_attributes['id'] = row[0]
            related.append({
                "target_node": target_node_attributes,
                "edge_attributes": {
                    "relationship": row[2],
                    "weight": row[3],
                    "confidence": row[4],
                    "provenance": row[5]
                }
            })
        return related

    def add_memory(self, memory_data: dict):
        cursor = self.connection.cursor()
        
        # Extract and serialize data
        best_match = memory_data.get('best_match', {})
        fusion_data = memory_data.get('fusion_data', {})
        aux_analysis = memory_data.get('auxiliary_analysis', {})

        params = (
            memory_data.get('id'),
            memory_data.get('timestamp'),
            memory_data.get('source_image_name'),
            json.dumps(memory_data.get('vector')),
            best_match.get('image_name'),
            best_match.get('score'),
            json.dumps(fusion_data.get('logical_terms')),
            json.dumps(aux_analysis.get('psyche_state')),
            aux_analysis.get('self_correlation_score')
        )

        cursor.execute('''
            INSERT INTO personal_memory (
                memory_id, timestamp, source_image_name, vector, best_match_id, 
                best_match_score, logical_terms, psyche_state, self_correlation_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', params)
        self.connection.commit()
        return cursor.lastrowid

    def get_all_memories(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM personal_memory ORDER BY timestamp ASC")
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                "id": row[1], # memory_id
                "timestamp": row[2],
                "source_image_name": row[3],
                "vector": json.loads(row[4]),
                "best_match": {
                    "image_name": row[5],
                    "score": row[6]
                },
                "fusion_data": {
                    "logical_terms": json.loads(row[7])
                },
                "auxiliary_analysis": {
                    "psyche_state": json.loads(row[8]),
                    "self_correlation_score": row[9]
                }
            })
        return memories

    def close(self):
        if self.connection:
            self.connection.close()

    def save(self):
        if self.connection:
            self.connection.commit()

    def add_vector(self, vector_id: str, vector: list, layer: str):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO vector_database (id, vector, layer)
            VALUES (?, ?, ?)
        ''', (vector_id, json.dumps(vector), layer))
        self.connection.commit()

    def get_all_vectors(self) -> tuple[list, list, list]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, vector, layer FROM vector_database")
        
        ids = []
        vectors = []
        layers = []
        for row in cursor.fetchall():
            ids.append(row[0])
            vectors.append(json.loads(row[1]))
            layers.append(row[2])
        return ids, vectors, layers

    def clear_vector_database(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM vector_database")
        self.connection.commit()
        print("Vector database cleared.")
