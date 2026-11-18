import json
from database.db_connection import create_connection
from pathlib import Path

JSON_PATH = Path(__file__).resolve().with_name('tasks.json')

with open(JSON_PATH, 'r') as file:
    tasks = json.load(file)
    
for index, task in enumerate(tasks):
    if"description" not in task:
        print(f"Task at index {index} is missing")
        print(task)
    
connection = create_connection()
cursor = connection.cursor()  #cursor is used to execute sql command

for task in tasks:
    task_id = task.get("id")
    name = task.get("name")
    description = task.get("description")
    due_date = task.get("due_date")
    cursor.execute(
        """INSERT OR IGNORE INTO tasks
        (id,
        name,
        description,
        due_date) VALUES (?, ?, ?, ?)""",
        (task_id, name, description, due_date)
    )

connection.commit()
cursor.execute("SELECT COUNT(*) FROM tasks")
total_tasks = cursor.fetchone()[0]
print(f"Total tasks in database: {total_tasks}")
print(f"Total tasks in JSON: {len(tasks)}")
print(f"Total tasks in SQLite: {total_tasks}")
connection.close()