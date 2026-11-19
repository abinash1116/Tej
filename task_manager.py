import json
from pathlib import Path
from time import strptime
from database.db_connection import create_connection

TASKS_FILE = Path(__file__).resolve().with_name("tasks.json")

def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            tasks = json.load(file)
            if not isinstance(tasks, list):
                tasks = []
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []
    return tasks


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)
    return tasks


def normalize_due_date(value):
    separator = "/" if "/" in value else "-"
    date_parts = value.split(separator)
    if (
        len(date_parts) != 3
        or len(date_parts[0]) != 4
        or len(date_parts[1]) != 2
        or len(date_parts[2]) != 2
        or not all(part.isdecimal() for part in date_parts)
    ):
        raise ValueError("Enter a date in YYYY/MM/DD or YYYY-MM-DD format.")

    year, month, day = (int(part) for part in date_parts)
    if year < 1 or not 1 <= month <= 12:
        raise ValueError("Year or month is outside the valid range.")

    if separator == "/":
        if not 1 <= day <= 32:
            raise ValueError("Nepali BS day must be between 1 and 32.")
    else:
        try:
            parsed_date = strptime(value, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError("Enter a valid Gregorian AD date.") from error
        year, month, day = (
            parsed_date.tm_year,
            parsed_date.tm_mon,
            parsed_date.tm_mday,
        )

    return f"{year:04d}{separator}{month:02d}{separator}{day:02d}"


def get_task_by_id(tasks, task_id):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def select_matching_task(matches, action):
    if len(matches) == 1:
        return matches[0]

    print("Multiple matching tasks found:")
    for task in matches:
        print(f"ID: {task.get('id', 'not assigned')} - {task['name']}")

    task_id = input(f"Enter the task ID to {action}: ").strip()
    try:
        selected_task_id = int(task_id)
    except ValueError:
        print("Invalid task ID. Enter a number.")
        return None

    selected_task = get_task_by_id(matches, selected_task_id)
    if selected_task is None:
        print("No matching task ID found.")
    return selected_task


def confirm_task_action(answer):
    return answer.strip().casefold() in ("yes", "y")

def remove_task(tasks, task):
    if task not in  tasks:
        print("Task not found in the list.")
        return False
    tasks.remove(task)
    return True

def update_task(tasks, task, field, new_values):
    if task not in tasks:
        return False
    task.update({field: new_values})
    return True

def assign_task_ids(tasks):
    used_ids = set()
    next_id = 1
    for task in tasks:
        task_id = task.get("id")
        if (
            isinstance(task_id, int)
            and not isinstance(task_id, bool)
            and task_id > 0
            and task_id not in used_ids
        ):
            used_ids.add(task_id)
            continue

        while next_id in used_ids:
            next_id += 1
        task["id"] = next_id
        used_ids.add(next_id)
        next_id += 1

def add_task_from_assistant(name, description = None, due_date= None):
    if not name or not name.strip():
        print("Task name cannot be empty. Please provide a valid task name.")
        return
    
    name = name.strip()
    
    if description is not None:
        description = description.strip() or None
    
    if due_date is not None:
        due_date = due_date.strip() or None
        
    if due_date is not None:
        due_date = normalize_due_date(due_date)
    
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
              INSERT INTO tasks(name, description, due_date) VALUES(?, ?, ?)
                             
        """,
        (name, description, due_date))
    
    task_id = cursor.lastrowid
    
    new_tasks = {
        'id': task_id,
        'name': name,
        'description': description,
        'due_date': due_date
    }
    connection.commit()
    connection.close()
    return new_tasks

def view_task_from_assistant():
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT * FROM tasks             
        """)
    tasks = [dict(task) for task in cursor.fetchall()]
    connection.close()
    return tasks


def search_task_from_assistant(name):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * from tasks WHERE name LIKE ?
    """, (f"%{name}%",))
    matches = [dict(task) for task in cursor.fetchall()]
    connection.close()
    return matches


def delete_task_from_assistant(task_id):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
    DELETE FROM tasks WHERE id = ?               
    """, (task_id,))
    deleted = cursor.rowcount
    
    connection.commit()
    connection.close()

    return deleted

def update_task_from_assistant(task_id, field, new_value):
    allowed_fields = ["name", "description", "due_date"]
    if field not in allowed_fields:
        return False
    if field == "due_date" and new_value is not None:
        new_value = normalize_due_date(new_value)
    connection = create_connection()
    cursor = connection.cursor()
    
    query = f"""
    UPDATE tasks
    SET {field} = ?
    WHERE id = ?
    """
    cursor.execute(query,(new_value, task_id))
    
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    return updated

