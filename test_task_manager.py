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
    normalize_due_date,
    add_task_from_assistant
    )

new_task = add_task_from_assistant(
    name = "Learn Python",
    description = "Complete Python course",
    due_date = "2083/08/01"
)

print("Task added successfully", new_task)