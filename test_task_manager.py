import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import task_manager

from task_manager import (
    get_task_by_id,
    assign_task_ids,
    remove_task,
    update_task,
    confirm_task_action,
    normalize_due_date
    )


class TestGetTaskById(unittest.TestCase):

    def test_existing_task_id(self):
        tasks = [
            {"id": 1, "title": "Learn Python"},
            {"id": 2, "title": "Build AI Assistant"}
        ]

        result = get_task_by_id(tasks, 2)

        self.assertEqual(result["title"], "Build AI Assistant")
        
    def test_non_existing_task_id(self):
        tasks = [
                    {"id": 1, "title": "Learn Python"},
                    {"id": 2, "title": "Build AI Assistant"}
                ]
        
        result = get_task_by_id(tasks, 99)
        
        self.assertIsNone(result)

    def test_empty_task_list(self):
        tasks = []
        result = get_task_by_id(tasks, 1)
        self.assertIsNone(result, "Task list is empty.")
        
        
class TestAssignTaskIds(unittest.TestCase):
    def test_assign_task_ids(self):
        tasks = [
            {"title": "Task 1"},
            {"title": "Task 2"}
        ]
        
        assign_task_ids(tasks)
        
        self.assertEqual(tasks[0]["id"],1)
        self.assertEqual(tasks[1]["id"],2)
        
    def test_task_ids_are_unique(self):
        tasks = [
                {"title": "Task 3"},
                {"title": "Task 4"}
        ]
            
        assign_task_ids(tasks)
            
        ids = [task["id"] for task in tasks]
        self.assertEqual(len(ids), len(set(ids)))
        
    def test_empty_task(self):
        tasks = []
        assign_task_ids(tasks)
        self.assertEqual(tasks, [])
        

class TestRemoveTask(unittest.TestCase):

    def test_removes_existing_task(self):
        task = {"id": 1, "name": "Learn Python"}
        tasks = [task]

        result = remove_task(tasks, task)

        self.assertTrue(result) #checks whether the function reports success.
        self.assertEqual(tasks, [])

    def test_missing_task_returns_false(self):
        tasks = [{"id": 1, "name": "Learn Python"}]
        missing_task = {"id": 2, "name": "Missing"}

        result = remove_task(tasks, missing_task)

        self.assertFalse(result)
        self.assertEqual(len(tasks), 1)

    def test_empty_task_list(self):
        tasks = []

        result = remove_task(tasks, {"id": 1})

        self.assertFalse(result)


class TestUpdateTask(unittest.TestCase):

    def test_updates_selected_field(self):
        task = {"id": 1, "name": "Old Name"}
        tasks = [task]

        result = update_task(tasks, task, "name", "New Name")

        self.assertTrue(result)
        self.assertEqual(task["name"], "New Name")

    def test_preserves_other_fields(self):
        task = {
            "id": 1,
            "name": "Learn Python",
            "description": "Practice daily"
        }
        tasks = [task]

        update_task(tasks, task, "name", "Learn SQL")

        self.assertEqual(task["name"], "Learn SQL")
        self.assertEqual(task["description"], "Practice daily")

    def test_missing_task_returns_false(self):
        tasks = [{"id": 1, "name": "Learn Python"}]
        missing_task = {"id": 2, "name": "Missing"}

        result = update_task(
            tasks, missing_task, "name", "New Name"
        )

        self.assertFalse(result)
        self.assertEqual(tasks[0]["name"], "Learn Python")



class TestConfirmTaskAction(unittest.TestCase):

    def test_accepts_yes(self):
        self.assertTrue(confirm_task_action("yes"))

    def test_accepts_y(self):
        self.assertTrue(confirm_task_action("Y"))

    def test_rejects_no(self):
        self.assertFalse(confirm_task_action("no"))

    def test_handles_whitespace(self):
        self.assertTrue(confirm_task_action("  yes  "))
        
class test_normalize_due_date(unittest.TestCase):
    def test_valid_nepali_date(self):
        result = normalize_due_date("2083/06/05")

        self.assertEqual(result, "2083/06/05")

    def test_valid_gregorian_date(self):
        result = normalize_due_date("2026-10-29")

        self.assertEqual(result, "2026-10-29")

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):
            normalize_due_date("29-10-2026")

    def test_invalid_gregorian_date(self):
        with self.assertRaises(ValueError):
            normalize_due_date("2026-02-30")

    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            normalize_due_date("2083/13/05")

    def test_invalid_nepali_day(self):
        with self.assertRaises(ValueError):
            normalize_due_date("2083/06/33")

class TemporaryTaskFileTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.tasks_file = Path(self.temp_dir.name) / "tasks.json"

        file_patch = patch.object(
            task_manager, "TASKS_FILE", self.tasks_file
        )
        file_patch.start()
        self.addCleanup(file_patch.stop)


# --------------------------------------------------
# Tests for load_tasks()
# --------------------------------------------------

class TestLoadTasks(TemporaryTaskFileTestCase):

    def test_loads_saved_tasks(self):
        expected = [{"id": 1, "name": "Learn Python"}]
        self.tasks_file.write_text(json.dumps(expected), encoding="utf-8")

        result = task_manager.load_tasks()

        self.assertEqual(result, expected)

    def test_missing_file_returns_empty_list(self):
        result = task_manager.load_tasks()

        self.assertEqual(result, [])

    def test_invalid_json_returns_empty_list(self):
        self.tasks_file.write_text("{invalid json", encoding="utf-8")

        result = task_manager.load_tasks()

        self.assertEqual(result, [])

    def test_non_list_json_returns_empty_list(self):
        self.tasks_file.write_text('{"name": "Learn Python"}', encoding="utf-8")

        result = task_manager.load_tasks()

        self.assertEqual(result, [])


# --------------------------------------------------
# Tests for save_tasks()
# --------------------------------------------------

class TestSaveTasks(TemporaryTaskFileTestCase):

    def test_saves_tasks_to_json(self):
        tasks = [{"id": 1, "name": "Learn Python"}]

        task_manager.save_tasks(tasks)

        saved_data = json.loads(
            self.tasks_file.read_text(encoding="utf-8")
        )
        self.assertEqual(saved_data, tasks)

    def test_saved_tasks_can_be_loaded_again(self):
        tasks = [{"id": 1, "name": "Study networking"}]

        task_manager.save_tasks(tasks)
        result = task_manager.load_tasks()

        self.assertEqual(result, tasks)


# --------------------------------------------------
# Tests for select_matching_task()
# --------------------------------------------------

class TestSelectMatchingTask(unittest.TestCase):

    def test_returns_single_match_without_input(self):
        task = {"id": 1, "name": "Learn Python"}

        result = task_manager.select_matching_task([task], "update")

        self.assertIs(result, task)

    def test_selects_correct_task_from_multiple_matches(self):
        tasks = [
            {"id": 1, "name": "Study"},
            {"id": 2, "name": "Study"}
        ]

        with patch("builtins.input", return_value="2"):
            result = task_manager.select_matching_task(tasks, "update")

        self.assertEqual(result["id"], 2)


# --------------------------------------------------
# Tests for add_task()
# --------------------------------------------------

class TestAddTask(TemporaryTaskFileTestCase):

    def test_adds_task_and_assigns_id(self):
        user_inputs = [
            "Learn Python",
            "Practice testing",
            "2026-10-30"
        ]

        with patch("builtins.input", side_effect=user_inputs):
            task_manager.add_task()

        saved_tasks = task_manager.load_tasks()

        self.assertEqual(len(saved_tasks), 1)
        self.assertEqual(saved_tasks[0]["id"], 1)
        self.assertEqual(saved_tasks[0]["name"], "Learn Python")
        self.assertEqual(
            saved_tasks[0]["description"], "Practice testing"
        )
        self.assertEqual(saved_tasks[0]["due_date"], "2026-10-30")


# --------------------------------------------------
# Tests for view_task()
# --------------------------------------------------

class TestViewTask(TemporaryTaskFileTestCase):

    def test_displays_saved_tasks(self):
        tasks = [{"id": 1, "name": "Learn Python"}]
        task_manager.save_tasks(tasks)

        output = StringIO()
        with redirect_stdout(output):
            task_manager.view_task()

        self.assertIn("Learn Python", output.getvalue())
        self.assertIn("Task ID: 1", output.getvalue())

    def test_displays_message_when_no_tasks_exist(self):
        output = StringIO()

        with redirect_stdout(output):
            task_manager.view_task()

        self.assertIn("No tasks found", output.getvalue())


# --------------------------------------------------
# Tests for search()
# --------------------------------------------------

class TestSearch(TemporaryTaskFileTestCase):

    def test_finds_task_case_insensitively(self):
        tasks = [{
            "id": 1,
            "name": "Learn Python",
            "description": "Practice",
            "due_date": "2026-10-30"
        }]
        task_manager.save_tasks(tasks)

        output = StringIO()
        with patch("builtins.input", return_value="learn python"):
            with redirect_stdout(output):
                task_manager.search()

        self.assertIn("Learn Python", output.getvalue())

    def test_displays_message_when_no_tasks_exist(self):
        output = StringIO()

        with redirect_stdout(output):
            task_manager.search()

        self.assertIn("No tasks found", output.getvalue())


# --------------------------------------------------
# Tests for delete()
# --------------------------------------------------

class TestDelete(TemporaryTaskFileTestCase):

    def test_deletes_task_after_confirmation(self):
        tasks = [{
            "id": 1,
            "name": "Learn Python",
            "description": "Practice",
            "due_date": "2026-10-30"
        }]
        task_manager.save_tasks(tasks)

        user_inputs = ["Learn Python", "yes"]

        with patch("builtins.input", side_effect=user_inputs):
            task_manager.delete()

        self.assertEqual(task_manager.load_tasks(), [])


# --------------------------------------------------
# Tests for update()
# --------------------------------------------------

class TestUpdate(TemporaryTaskFileTestCase):

    def test_updates_task_name_and_saves_it(self):
        tasks = [{
            "id": 1,
            "name": "Learn Python",
            "description": "Practice",
            "due_date": "2026-10-30"
        }]
        task_manager.save_tasks(tasks)

        user_inputs = [
            "Learn Python",  # Find task
            "yes",           # Confirm update
            "name",          # Field to update
            "Learn SQL"      # New name
        ]

        with patch("builtins.input", side_effect=user_inputs):
            task_manager.update()

        saved_tasks = task_manager.load_tasks()

        self.assertEqual(saved_tasks[0]["name"], "Learn SQL")
        self.assertEqual(saved_tasks[0]["description"], "Practice")
        self.assertEqual(saved_tasks[0]["id"], 1)


if __name__ == "__main__":
    unittest.main()