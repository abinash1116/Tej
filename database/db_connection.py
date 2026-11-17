import sqlite3
from pathlib import Path

DB_Path = Path(__file__).resolve().with_name("task.db")

def create_connection():
    connection = sqlite3.connect(DB_Path)
    connection.row_factory = sqlite3.Row
    return connection

def create_task_table():
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tasks(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       description TEXT,
                       due_date TEXT
                   )
            """)
    connection.commit()
    connection.close()
    