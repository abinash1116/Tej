from gemini_client import generate_response, analyze_user_prompt
from conversation_manager import load_conversation_history, add_message
from task_manager import add_task_from_assistant, view_task_from_assistant, search_task_from_assistant, update_task_from_assistant, delete_task_from_assistant, load_tasks, get_task_by_id, confirm_task_action
def start_assistant():
    print(" Welcome to Tej AI Assistant!..")
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
        if analysis is None:
            print("Sorry, I couldn't understant your request. Please try again.")
            continue
        
        intent = analysis.get("intent", "unknown")
        
        if intent == "unknown":
            response = generate_response(user_input, history)
            if response is None:
                print("Sorry, I couldn't generate a response. Please try again.")
                continue
        
            add_message(history, "user", user_input)
            add_message(history, "model", response)
            print("\nTej: ",response)
            print()
        else:
            print("\nTask Command Detected!")
            print("Intent: ",intent)
            entities = analysis.get("entities", {})
            
            if intent == "add_task":
                try:
                    name = entities.get("name")
                    description = entities.get("description")
                    due_date = entities.get("due_date")
        
                    if intent == "add_task" and name:
                        new_task = add_task_from_assistant(
                            name=name,
                            description=description,
                            due_date=due_date
                        )
                        print("Task added successfully:", new_task)
                except ValueError as e:
                    print("Unable to add task:", e)
                    
            if intent == "view_tasks":
                print("Viewing tasks...")
                tasks = view_task_from_assistant()
                    
                if not tasks:
                    print("No tasks found.")
                    pass
                else:
                    for task in tasks:
                        print(
                            f"Task ID: {task.get('id')}", 
                            f"Name: {task.get('name')}", 
                            f"description: {task.get('description')}",
                            f"due_date: {task.get('due_date')}"
                        )
            
            if intent == "search_tasks":
                search_name = entities.get("name")

                if not search_name:
                        print("No matching tasks found.")
                    
                else:
                    print(f"Searcing for task {search_name}")
                    matches = search_task_from_assistant(search_name)
                    
                    if not matches:
                        print("No matching task found.")
                    else:
                        print("Matching task found.")
                        for task in matches:
                            print(
                            f"Task Id: {task.get('id')}",
                            f"Name: {task.get('name')}",
                            f"Description: {task.get('description')}",
                            f"Due_Date: {task.get('due_date')}"
                            )
            if intent == "delete_task":
                task_id = entities.get("task_id")
                task_name = entities.get("name")

                matches = []

                if task_id is not None:
                    try:
                        task_id = int(task_id)
                    except (ValueError, TypeError):
                        print("Invalid task ID.")
                        continue

                    task = get_task_by_id(load_tasks(), task_id)

                    if task:
                        matches = [task]

                elif task_name:
                    matches = search_task_from_assistant(task_name)

                if not matches:
                    print("No matching task found.")
                    continue

                if len(matches) > 1:
                    print("Multiple matching tasks found:")

                    for task in matches:
                        print(f"ID: {task.get('id')} - {task.get('name')}")

                    try:
                        selected_id = int(input("Enter the task ID to delete: "))
                    except ValueError:
                        print("Invalid task ID.")
                        continue

                    if not any(task["id"] == selected_id for task in matches):
                        print("Invalid selection.")
                        continue

                    task_id = selected_id

                else:
                    task_id = matches[0]["id"]

                selected_task = get_task_by_id(load_tasks(), task_id)

                print(f"Task selected: {selected_task['name']}")

                answer = input("Are you sure you want to delete this task? (Yes/No): ")

                if confirm_task_action(answer):
                    deleted_task = delete_task_from_assistant(task_id)

                    if deleted_task:
                        print(f"Task deleted successfully: {deleted_task['name']}")
                    else:
                        print("Unable to delete task.")
                else:
                    print("Task deletion cancelled.")
    
            if intent == "update_task":
                task_id = entities.get("task_id")
                task_name = entities.get("name")
                field = entities.get("field")
                new_value = entities.get("new_value")

                matches = []

                if task_id is not None:
                    try:
                        task_id = int(task_id)
                    except (ValueError, TypeError):
                        print("Invalid task ID.")
                        continue

                    task = get_task_by_id(load_tasks(), task_id)

                    if task:
                        matches = [task]

                elif task_name:
                    matches = search_task_from_assistant(task_name)

                if not matches:
                    print("No matching task found.")
                    continue

                if len(matches) > 1:
                    print("Multiple matching tasks found:")

                    for task in matches:
                        print(f"ID: {task.get('id')} - {task.get('name')}")

                    try:
                        selected_id = int(input("Enter the task ID to update: "))
                    except ValueError:
                        print("Invalid task ID.")
                        continue

                    if not any(task["id"] == selected_id for task in matches):
                        print("Invalid selection.")
                        continue

                    task_id = selected_id

                else:
                    task_id = matches[0]["id"]

                if field not in ("name", "description", "due_date"):
                    print("Invalid update field.")
                    continue

                if not new_value:
                    print("Please provide the new value.")
                    continue

                selected_task = get_task_by_id(load_tasks(), task_id)

                print(f"Task: {selected_task['name']}")
                print(f"Field to update: {field}")
                print(f"New value: {new_value}")

                answer = input("Are you sure you want to update this task? (Yes/No): ")

                if confirm_task_action(answer):
                    try:
                        updated_task = update_task_from_assistant(
                            task_id,
                            field,
                            new_value
                        )

                        if updated_task:
                            print("Task updated successfully!")
                            print(updated_task)

                    except ValueError as error:
                        print("Unable to update task:", error)

                else:
                    print("Task update cancelled.")                        
if __name__ == "__main__":
    start_assistant()