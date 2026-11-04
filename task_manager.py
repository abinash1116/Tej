import json
from pathlib import Path
from time import strptime

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


def add_task():
    while True:
        task_name = input("Enter the task name: ").strip()
        if task_name:
            break
        print("Task name cannot be empty, Please enter a valid task name.")
    while True:
        task_description= input("Enter the task description: ").strip()
        if task_description:
                break
        print("Task description cannot be empty, Please enter a valid task description.")
    while True:
        task_due_date = input(
            "Enter due date: YYYY/MM/DD for Nepali BS or YYYY-MM-DD for Gregorian AD: "
        ).strip()
        if not task_due_date:
            print("Task due date cannot be empty. Please enter a valid task due date.")
            continue
        try:
            task_due_date = normalize_due_date(task_due_date)
        except ValueError:
            print("Invalid date. Use YYYY/MM/DD (Nepali BS, day 1-32) or YYYY-MM-DD (Gregorian AD).")
            continue
        break

    new_task = {
        "name": task_name,
        "description": task_description,
        "due_date": task_due_date,
    }

    tasks = load_tasks()
    assign_task_ids(tasks)
    task_id = max((task["id"] for task in tasks), default=0) + 1

    new_task["id"] = task_id
    tasks.append(new_task)

    save_tasks(tasks)  #write python data to a json file with indentation for readability
    print(f"Task added with ID: {task_id}")
    
    
def view_task():
    tasks = load_tasks()

    try:
        if not tasks:
            print("No tasks found")
            
        for task in tasks:
            print(f" Task ID: {task.get('id', 'not assigned')}")
            print(f"Task name: {task['name']}")
    except KeyError as e:
        print(f"Error: Missing key in task data - {e}")

def search():
    tasks = load_tasks()
    if not tasks:
            print("No tasks found,")
            return
    search_name = input("Enter the task name you are searching for: ").strip().casefold()
    matches = [
        task for task in tasks
        if task["name"].casefold() == search_name
    ]

    if not matches:
        print("No matching task found.")
        return

    selected_task = select_matching_task(matches, "search")
    
    if selected_task is None:
        return

    print(
        f"Task details:\n"
        f"ID: {selected_task.get('id', 'not assigned')}\n"
        f"Name: {selected_task['name']}\n"
        f"Description: {selected_task['description']}\n"
        f"Due Date: {selected_task['due_date']}"
    )

def delete():
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    task_name = input("Enter the task name you want to delete: ").strip().casefold()
    matches = [
        task for task in tasks
        if task["name"].casefold() == task_name
    ]
    if not matches:
        print("No matching task found.")
        return

    matching_task_count = len(matches)
    if matching_task_count > 1:
        print(f"{matching_task_count} matching tasks found:")
        for task in matches:
            print(f"ID: {task.get('id', 'not assigned')} - {task['name']}")

        task_id = input("Enter the task ID to delete: ").strip()
        try:
            selected_task_id = int(task_id)
        except ValueError:
            print("Invalid task ID. Enter a number.")
            return
        task_to_delete = get_task_by_id(matches, selected_task_id)
        if task_to_delete is None:
            print("No matching task ID found.")
            return
    else:
        task_to_delete = matches[0]

    answer = input("Are you sure to delete the task? (Yes/No): ").strip().casefold()
    if not confirm_task_action(answer):
        print("Task deletion cancelled.")
        return

    if remove_task(tasks, task_to_delete):
        save_tasks(tasks)
        print(f"Task deleted: ID {task_to_delete.get('id')} - {task_to_delete['name']}")
    else:
        print("Task not found in the list. Deletion failed.")

def update():
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    task_name = input("Enter the task name you want to update: ").strip().casefold()
    matches = [
        task for task in tasks
        if task["name"].casefold() == task_name
    ]
    if not matches:
        print("No matching task found.")
        return

    task_to_update = select_matching_task(matches, "update")
    if task_to_update is None: 
        return
    
    answer = input("Are you sure to update the task: (Yes/No): ").strip().casefold()
    if not confirm_task_action(answer):
        print("Task update cancelled.")
        return
    field = input(
        "Which field do you want to update (name, description, due_date)? "
    ).strip().casefold()
    if field not in ("name", "description", "due_date"):
        print("Invalid field. Choose name, description, or due_date.")
        return
    field_label = field.replace("_", " ")
    current_value = str(task_to_update.get(field, "")).strip().casefold()
    while True:
        new_value = input(f"Enter the new {field_label}: ").strip()
        if new_value == "":
            print(f"{field_label.capitalize()} cannot be empty. Please enter a valid {field_label}.")
            continue
        if new_value.casefold() == current_value:
            print(
                f"The {field_label} is the same as before. "
                f"Please enter a new {field_label}."
            )
            continue
        if field == "due_date":
            try:
                new_value = normalize_due_date(new_value)
            except ValueError:
                print("Invalid date. Use YYYY/MM/DD (Nepali BS, day 1-32) or YYYY-MM-DD (Gregorian AD).")
                continue
        update_task(tasks, task_to_update, field, new_value)
        break

    save_tasks(tasks)
    print(f"Task {field_label} updated.")
