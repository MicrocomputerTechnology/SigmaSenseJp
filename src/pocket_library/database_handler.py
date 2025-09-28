import sqlite3
import os

class DatabaseHandler:
    """Handles connections to and queries for SQLite-based dictionaries."""

    def __init__(self, db_path: str):
        """
        Initializes the database handler and connects to the database.

        Args:
            db_path: The path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = None
        if not os.path.exists(self.db_path):
            print(f"Database file not found at: {self.db_path}")
        else:
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            except sqlite3.Error as e:
                print(f"Error connecting to database: {e}")

    def lookup_word(self, word: str) -> list[tuple]:
        """
        Looks up a word in the EJDict-hand database.

        Args:
            word: The word to look up.

        Returns:
            A list of tuples containing the search results (word, definition).
        """
        if not self.connection:
            print("Database connection not available.")
            return []
        
        results = []
        try:
            cursor = self.connection.cursor()
            # The table is named 'items' and columns are 'word' and 'mean'
            cursor.execute("SELECT word, mean FROM items WHERE word = ?", (word,))
            results = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error during database lookup: {e}")
        
        return results

    def close(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

# Example usage:
if __name__ == '__main__':
    # Assumes the script is run from the project root
    db_file_path = os.path.join("data", "ejdict.sqlite3")
    
    handler = DatabaseHandler(db_file_path)
    if handler.connection:
        word_to_lookup = "persistent"
        print(f"Looking up word: '{word_to_lookup}'")
        search_results = handler.lookup_word(word_to_lookup)
        
        if search_results:
            for row in search_results:
                print(f"  Word: {row[0]}")
                print(f"  Meaning: {row[1]}")
        else:
            print("Word not found.")
        
        handler.close()