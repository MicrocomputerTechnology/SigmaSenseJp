import sqlite3
import os
from datetime import datetime, UTC

class ProperNounStore:
    """A specialized store for proper nouns and their inferred categories."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        dir_name = os.path.dirname(db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.connection.cursor()
        # Table for proper nouns and their associated categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proper_nouns (
                proper_noun TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                provenance TEXT,
                last_updated TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_proper_noun ON proper_nouns (proper_noun)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON proper_nouns (category)')
        self.connection.commit()

    def add_proper_noun(self, proper_noun: str, category: str, provenance: str = 'inferred'):
        cursor = self.connection.cursor()
        last_updated = datetime.now(UTC).isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO proper_nouns (proper_noun, category, provenance, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (proper_noun, category, provenance, last_updated))
        self.connection.commit()

    def get_category(self, proper_noun: str) -> str | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT category FROM proper_nouns WHERE proper_noun = ?", (proper_noun,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_proper_nouns_by_category(self, category: str) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT proper_noun FROM proper_nouns WHERE category = ?", (category,))
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        if self.connection:
            self.connection.close()

    def save(self):
        if self.connection:
            self.connection.commit()
