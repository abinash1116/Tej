
from task_manager import (
    add_task_from_assistant,
    view_task_from_assistant,
    search_task_from_assistant,
    update_task_from_assistant,
    delete_task_from_assistant,
    confirm_task_action,
)
from database.db_connection import create_task_table


def display_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        print(
            f"\nTask ID: {task['id']}\n"
            f"Name: {task['name']}\n"
            f"Description: {task['description']}\n"
            f"Due Date: {task['due_date']}\n"
        )


def add_task():
    name = input("Enter task name: ")
    description = input("Enter task description: ") or None
    due_date = input("Enter due date (optional): ") or None

    try:
        task = add_task_from_assistant(name, description, due_date)

        if task:
            print("Task added successfully:", task)

    except ValueError as error:
        print("Unable to add task:", error)


def view_tasks():
    tasks = view_task_from_assistant()
    display_tasks(tasks)


def search_tasks():
    name = input("Enter task name to search: ").strip()

    if not name:
        print("Please enter a task name.")
        return

    matches = search_task_from_assistant(name)
    display_tasks(matches)


def update_task():
    tasks = view_task_from_assistant()

    if not tasks:
        print("No tasks available to update.")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("Enter task ID to update: "))
    except ValueError:
        print("Invalid task ID.")
        return

    selected_task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if selected_task is None:
        print("Task not found.")
        return

    print("Fields: name, description, due_date")
    field = input("Enter field to update: ").strip().casefold()

    if field not in ("name", "description", "due_date"):
        print("Invalid field.")
        return

    new_value = input("Enter new value: ").strip()

    if not new_value:
        print("New value cannot be empty.")
        return

    answer = input("Confirm update? (Yes/No): ")

    if not confirm_task_action(answer):
        print("Update cancelled.")
        return

    try:
        updated = update_task_from_assistant(
            task_id,
            field,
            new_value
        )

        if updated:
            print("Task updated successfully!")
        else:
            print("Unable to update task.")

    except ValueError as error:
        print("Unable to update task:", error)


def delete_task():
    tasks = view_task_from_assistant()

    if not tasks:
        print("No tasks available to delete.")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("Enter task ID to delete: "))
    except ValueError:
        print("Invalid task ID.")
        return

    selected_task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if selected_task is None:
        print("Task not found.")
        return

    answer = input(
        f"Are you sure you want to delete "
        f"'{selected_task['name']}'? (Yes/No): "
    )

    if not confirm_task_action(answer):
        print("Deletion cancelled.")
        return

    deleted = delete_task_from_assistant(task_id)

    if deleted:
        print("Task deleted successfully!")
    else:
        print("Unable to delete task.")


def main():
    print("Welcome to the task manager!")

    create_task_table()

    while True:
        print("\nTASK MANAGER")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Search Tasks")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Exit")

        choice = input("\nChoose an option: ").strip().casefold()

        if choice in ("1", "add task"):
            add_task()

        elif choice in ("2", "view tasks"):
            view_tasks()

        elif choice in ("3", "search tasks"):
            search_tasks()

        elif choice in ("4", "update tasks"):
            update_task()

        elif choice in ("5", "delete tasks"):
            delete_task()

        elif choice in ("6", "exit"):
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()
