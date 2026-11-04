from task_manager import (
    add_task,
    assign_task_ids,
    delete,
    load_tasks,
    save_tasks,
    search,
    update,
    view_task,
)


def main():
    print("Welcome to the task manager")

    tasks = load_tasks()
    assign_task_ids(tasks)
    save_tasks(tasks)

    while True:
        choice = input(
            "Do you want to add, view, search, delete, update or exit? "
        ).strip().casefold()

        if choice == "exit":
            print("Goodbye!")
            break
        elif choice == "add":
            add_task()
        elif choice == "view":
            view_task()
        elif choice == "search":
            search()
        elif choice == "update":
            update()
        elif choice == "delete":
            delete()
        else:
            print("Invalid choice. Please enter add, view, search, update, delete, or exit.")


if __name__ == "__main__":
    main()
