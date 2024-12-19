import sqlite3
from assets.config import DB_PATH


class DataBase:
    def __init__(self) -> None:
        self.conn = None
        self.init_db()  # Initialize the database when the class is instantiated

    def init_db(self) -> None:
        """Initialize the database and create the necessary tables if they don't exist."""
        self.conn = sqlite3.connect(DB_PATH)
        cursor = self.conn.cursor()
        cursor.execute(""" 
                    CREATE TABLE IF NOT EXISTS state 
                        (key TEXT PRIMARY KEY, 
                        value TEXT)
                    """)

        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS game_state 
                        (key TEXT PRIMARY KEY, 
                        value TEXT)
                    """)
        self.conn.commit()
        self.conn.close()

    def set_value_state(self, key: str, value: str) -> None:
        """Set the value of a state key in the database.

        Args:
            key (str): The key for the state.
            value (str): The value to be associated with the key.
        """
        try:
            self.conn = sqlite3.connect(DB_PATH)
            cursor = self.conn.cursor()
            cursor.execute(
                "REPLACE INTO state (key, value) VALUES (?, ?)", (key, value)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error setting value state:", e)
        finally:
            if self.conn:
                self.conn.close()

    def get_value_state(self, key: str):
        """Retrieve the value associated with a state key from the database.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            str: The value associated with the key, or None if the key does not exist.
        """
        try:
            self.conn = sqlite3.connect(DB_PATH)
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM state WHERE key = ?", (key,))
            value = cursor.fetchone()

            return value[0] if value else None
        except sqlite3.Error as e:
            print("Error retrieving VALUE STATE from the data base:", e)
        finally:
            if self.conn:
                self.conn.close()

    def set_value_game_state(self, key: str, value: str) -> None:
        """Set the value of a game state key in the database.

        Args:
            key (str): The key for the game state.
            value (str): The value to be associated with the key.
        """
        try:
            self.conn = sqlite3.connect(DB_PATH)
            cursor = self.conn.cursor()
            cursor.execute(
                "REPLACE INTO game_state (key, value) VALUES (?, ?)", (key, value)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error setting game state:", e)
        finally:
            if self.conn:
                self.conn.close()

    def get_value_game_state(self, key: str):
        """Retrieve the value associated with a game state key from the database.

        Args:
            key (str): The key for which to retrieve the game state value.

        Returns:
            str: The value associated with the key, or None if the key does not exist.
        """
        try:
            self.conn = sqlite3.connect(DB_PATH)
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM game_state WHERE key = ?", (key,))
            value = cursor.fetchone()

            return value[0] if value else None
        except sqlite3.Error as e:
            print("Error get value game state:", e)
        finally:
            if self.conn:
                self.conn.close()
