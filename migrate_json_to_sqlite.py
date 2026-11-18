import json
from database.db_connection import create_connection
from pathlib import Path

JSON_PATH = Path(__file__).resolve().with_name('tasks.json')

with open(JSON_PATH, 'r') as file:
    tasks = json.load(file)
    
connection = create_connection()
cursor = connection.cursor()  #cursor is used to execute sql command

for task in tasks:
    id = task["id"]
    name = task["name"]
    description = task["description"]
    due_date = task["due_date"]
    cursor.execute(
        """INSERT INTO tasks
        (id,
        name,
        description,
        due_date) VALUES (?, ?, ?, ?)""",
        (id, name, description, due_date)
    )

connection.commit()
connection.close()