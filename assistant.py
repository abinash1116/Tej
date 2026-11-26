
from gemini_client import generate_response, analyze_user_prompt
from conversation_manager import load_conversation_history, add_message

from task_manager import (
    add_task_from_assistant,
    view_task_from_assistant,
    search_task_from_assistant,
    update_task_from_assistant,
    delete_task_from_assistant,
    confirm_task_action
)


def find_task_matches(task_id=None, task_name=None):
    """
    Find tasks using SQLite.
    If an ID is provided, search by ID.
    Otherwise, search by task name.
    """

    if task_id is not None:
        try:
            task_id = int(task_id)
        except (ValueError, TypeError):
            print("Invalid task ID.")
            return None

        tasks = view_task_from_assistant()

        matches = [
            task for task in tasks
            if task["id"] == task_id
        ]

        return matches

    if task_name:
        return search_task_from_assistant(task_name)

    return []


def select_task(matches, action):
    """Select one task from the matching results."""

    if not matches:
        print("No matching task found.")
        return None

    if len(matches) == 1:
        return matches[0]

    print("Multiple matching tasks found:")

    for task in matches:
        print(f"ID: {task['id']} - {task['name']}")

    try:
        selected_id = int(input(f"Enter the task ID to {action}: "))
    except ValueError:
        print("Invalid task ID.")
        return None

    for task in matches:
        if task["id"] == selected_id:
            return task

    print("Invalid selection.")
    return None

def validate_analysis(analysis):
    """
    Validate the structure of Gemini's analysis response.
    """
    
    supported_intents = {
        "add_tasks",
        "view_tasks",
        "search_tasks",
        "update_tasks",
        "delete_tasks",
        "complete_tasks",
        "unknown"
    }
    
    if not isinstance(analysis, dict):
        print("Invalid analysis response.")
        return None
    
    intent = analysis.get("intent")
    entities = analysis.get("entities")
    
    if not isinstance(intent, str) or intent not in supported_intents:
        print("Unsupported intent.")
        return None
    
    if not isinstance(entities, dict):
        print("Invalid entities structure.")
        return None
    
    return intent, entities

def start_assistant():
    print("Welcome to Tej AI Assistant!..")
    print("How can I help you today?")
    print("Ask me anything or type 'exit' to quit.")

    history = load_conversation_history()

    while True:
        user_input = input("You: ")

        if not user_input.strip():
            print("Please enter a valid prompt.")
            continue

        if user_input.casefold() == "exit":
            print("Goodbye!")
            break

        analysis = analyze_user_prompt(user_input)
        print("Gemini Analysis:", analysis)

        validated = validate_analysis(analysis)
        
        if validated is None:
            print("Sorry, I couldn't undertsant your request. Please try again.")
            continue
        
        intent, entities = validated

        if intent == "unknown":
            response = generate_response(user_input, history)

            if response is None:
                print("Sorry, I couldn't generate a response. Please try again.")
                continue

            add_message(history, "user", user_input)
            add_message(history, "model", response)

            print("\nTej:", response)
            print()
            continue

        print("\nTask Command Detected!")
        print("Intent:", intent)

        if intent == "add_task":
            try:
                name = entities.get("name")
                description = entities.get("description")
                due_date = entities.get("due_date")

                if not name:
                    print("Please provide a task name.")
                    continue

                new_task = add_task_from_assistant(
                    name=name,
                    description=description,
                    due_date=due_date
                )

                if new_task:
                    print("Task added successfully:", new_task)
                else:
                    print("Unable to add task.")

            except ValueError as error:
                print("Unable to add task:", error)

        elif intent == "view_tasks":
            print("Viewing tasks...")

            tasks = view_task_from_assistant()

            if not tasks:
                print("No tasks found.")
                continue

            for task in tasks:
                print(
                    f"Task ID: {task['id']}\n"
                    f"Name: {task['name']}\n"
                    f"Description: {task['description']}\n"
                    f"Due Date: {task['due_date']}\n"
                )

        elif intent == "search_tasks":
            search_name = entities.get("name")

            if not search_name:
                print("Please provide a task name to search.")
                continue

            print(f"Searching for task: {search_name}")

            matches = search_task_from_assistant(search_name)

            if not matches:
                print("No matching task found.")
                continue

            print("Matching tasks found:")

            for task in matches:
                print(
                    f"Task ID: {task['id']}\n"
                    f"Name: {task['name']}\n"
                    f"Description: {task['description']}\n"
                    f"Due Date: {task['due_date']}\n"
                )

        elif intent == "delete_task":
            task_id = entities.get("task_id")
            task_name = entities.get("name")

            matches = find_task_matches(
                task_id=task_id,
                task_name=task_name
            )

            if matches is None:
                continue

            selected_task = select_task(matches, "delete")

            if selected_task is None:
                continue

            print(f"Task selected: {selected_task['name']}")

            answer = input(
                "Are you sure you want to delete this task? (Yes/No): "
            )

            if confirm_task_action(answer):
                deleted = delete_task_from_assistant(selected_task["id"])

                if deleted:
                    print(
                        f"Task deleted successfully: "
                        f"{selected_task['name']}"
                    )
                else:
                    print("Unable to delete task. It may no longer exist.")

            else:
                print("Task deletion cancelled.")

        elif intent == "update_task":
            task_id = entities.get("task_id")
            task_name = entities.get("name")
            field = entities.get("field")
            new_value = entities.get("new_value")

            matches = find_task_matches(
                task_id=task_id,
                task_name=task_name
            )

            if matches is None:
                continue

            selected_task = select_task(matches, "update")

            if selected_task is None:
                continue

            if field not in ("name", "description", "due_date"):
                print("Invalid update field.")
                continue

            if new_value is None or (
                isinstance(new_value, str) and not new_value.strip()
            ):
                print("Please provide the new value.")
                continue

            print(f"Task: {selected_task['name']}")
            print(f"Field to update: {field}")
            print(f"New value: {new_value}")

            answer = input(
                "Are you sure you want to update this task? (Yes/No): "
            )

            if confirm_task_action(answer):
                try:
                    updated = update_task_from_assistant(
                        selected_task["id"],
                        field,
                        new_value
                    )

                    if updated:
                        print("Task updated successfully!")

                        updated_tasks = view_task_from_assistant()

                        for task in updated_tasks:
                            if task["id"] == selected_task["id"]:
                                print("Updated task:", task)
                                break
                    else:
                        print("Unable to update task. It may no longer exist.")

                except ValueError as error:
                    print("Unable to update task:", error)

            else:
                print("Task update cancelled.")

        else:
            print("Sorry, I don't recognize that task command.")


if __name__ == "__main__":
    start_assistant()
