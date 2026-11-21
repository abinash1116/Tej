
import sqlite3
import unittest
from database.db_connection import create_connection


class TestDatabase(unittest.TestCase): #unittest.TestCase gives us the structure for writing automated tests

    def test_create_connection(self):
        connection = create_connection()
        self.assertIsInstance(connection, sqlite3.Connection)
        connection.close()

    def test_row_factory(self):
        connection = create_connection()
        self.assertIs(connection.row_factory, sqlite3.Row)
        connection.close()

if __name__ == "__main__":
    unittest.main()
