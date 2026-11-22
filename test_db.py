
import sqlite3
import unittest
from database.db_connection import create_connection, create_task_table
import tempfile
from pathlib import Path
from unittest.mock import patch

class TestDatabase(unittest.TestCase): #unittest.TestCase gives us the structure for writing automated tests

    def test_create_connection(self):
        connection = create_connection()
        self.assertIsInstance(connection, sqlite3.Connection)
        connection.close()

    def test_row_factory(self):
        connection = create_connection()
        self.assertIs(connection.row_factory, sqlite3.Row)
        connection.close()
        
    def test_create_task_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_task.db"
            with patch("database.db_connection.create_connection") as mock_connection:
                connection = sqlite3.connect(db_path)
                mock_connection.return_value = connection
                create_task_table()
                mock_connection.assert_called_once()
                check_connection = sqlite3.connect(db_path)
                cursor = check_connection.cursor()
                cursor.execute("""
                            SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'tasks'
                            """)
                result = cursor.fetchone() #fetchone returns rows if table exists else returns none
                self.assertIsNotNone(result)
                cursor.execute("PRAGMA table_info(tasks)")
                columns = cursor.fetchall()

                column_names = [column[1] for column in columns]

                self.assertEqual(
                    column_names,
                    ["id", "name", "description", "due_date"]
                )
                check_connection.close()
    
    def test_create_task_table_twice(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_task.db"

            with patch("database.db_connection.create_connection") as mock_connection:
                mock_connection.side_effect = lambda: sqlite3.connect(db_path)

                create_task_table()
                create_task_table()

                self.assertEqual(mock_connection.call_count, 2)

            check_connection = sqlite3.connect(db_path)
            cursor = check_connection.cursor()

            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name = 'tasks'
            """)

            result = cursor.fetchone()
            self.assertIsNotNone(result)

            check_connection.close()

                
if __name__ == "__main__":
    unittest.main()
