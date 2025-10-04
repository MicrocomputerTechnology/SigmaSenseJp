import json
from hoho.pocket_library.database_handler import DatabaseHandler

class ExternalMembersDB(DatabaseHandler):
    def __init__(self, db_path: str = "data/external_members.sqlite3"):
        super().__init__(db_path)
        self._create_table()

    def _create_table(self):
        if not self.connection:
            return
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS external_members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                member_type TEXT,
                skills TEXT,
                availability TEXT,
                attributes TEXT
            )
        ''')
        self.connection.commit()

    def add_member(self, member_data: dict):
        if not self.connection:
            return
        cursor = self.connection.cursor()
        member_id = member_data.get("member_id")
        name = member_data.get("name")
        member_type = member_data.get("member_type")
        skills = json.dumps(member_data.get("skills", []))
        availability = member_data.get("availability")
        attributes = json.dumps(member_data.get("attributes", {}))
        
        cursor.execute('''
            INSERT OR REPLACE INTO external_members (member_id, name, member_type, skills, availability, attributes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (member_id, name, member_type, skills, availability, attributes))
        self.connection.commit()

    def get_member(self, member_id: str):
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM external_members WHERE member_id = ?", (member_id,))
        row = cursor.fetchone()
        if row:
            return {
                "member_id": row[0],
                "name": row[1],
                "member_type": row[2],
                "skills": json.loads(row[3]),
                "availability": row[4],
                "attributes": json.loads(row[5])
            }
        return None
