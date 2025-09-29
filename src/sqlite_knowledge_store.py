import sqlite3
import json
import os
from datetime import datetime, UTC
from .knowledge_store_base import KnowledgeStoreBase

class SQLiteStore(KnowledgeStoreBase):
    """SQLite-backed implementation of the KnowledgeStore."""

    def __init__(self, db_path: str):
        self.db_path = db_path
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
        # Indexes for fast traversal
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON edges (source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON edges (target_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_relationship ON edges (relationship)')
        self.connection.commit()

    def add_node(self, node_id: str, **attributes):
        cursor = self.connection.cursor()
        # Separate core attributes from the JSON blob
        domain = attributes.pop('domain', None)
        provenance = attributes.pop('provenance', 'manual')
        last_updated = datetime.now(UTC).isoformat()
        
        # Serialize remaining attributes to JSON
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
        if relationship:
            cursor.execute("""
                SELECT e.target_id, n.attributes, e.relationship, e.weight, e.confidence, e.provenance
                FROM edges e JOIN nodes n ON e.target_id = n.id
                WHERE e.source_id = ? AND e.relationship = ?
            """, (source_id, relationship))
        else:
            cursor.execute("""
                SELECT e.target_id, n.attributes, e.relationship, e.weight, e.confidence, e.provenance
                FROM edges e JOIN nodes n ON e.target_id = n.id
                WHERE e.source_id = ?
            """, (source_id,))
        
        related = []
        for row in cursor.fetchall():
            target_node_attributes = json.loads(row[1])
            target_node_attributes['id'] = row[0] # Ensure id is in the node dict
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

    def close(self):
        if self.connection:
            self.connection.close()

    def save(self):
        # For SQLite, commit is sufficient. This method is for API consistency.
        if self.connection:
            self.connection.commit()