from google import genai
import os
from dotenv import load_dotenv
from google.genai import errors
import json
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

api_key = os.getenv("Gemini_API_Key")

if not api_key:
    raise ValueError("API key not found.")

client = genai.Client(api_key = api_key)



def generate_response(prompt, history = None):
    if history is None:
        history = []
        
    contents = []
    
    for message in history:
        contents.append({
            "role": message["role"],
            "parts": [{"text": message["content"]}]
        })
        
    contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
    })
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
            contents=contents
    )
    return response.text
    
    
def analyze_user_prompt(user_input):
    current_date = datetime.now(
    ZoneInfo("Asia/Kathmandu")
).strftime("%Y-%m-%d")
    analysis_prompt = f"""
        You are Tej's Natural Language Task Command Analyzer.

        Your job is to understand the user's task-management request
        and extract the relevant information.

        SUPPORTED INTENTS AND THEIR MEANINGS:

        1. add_task:
        The user wants to create a new task.

        2. view_tasks:
        The user wants to see all saved tasks.

        3. search_tasks:
        The user wants to find a task using its name.

        4. update_task:
        The user wants to modify an existing task.

        5. delete_task:
        The user wants to delete an existing task.
        
        6. complete_task:
        The user wants to mark an existing task as completed.

        7. unknown:
        The request does not match any supported intent.
        

        ENTITY EXTRACTION RULES:

        For add_task:
        - Extract name, description, and due_date.
        - Missing information must be null.
        - Do not invent task details.

        For search_tasks:
        - Extract the task name as name.
        - Missing name must be null.

        For update_task:
        - Extract task_id if explicitly provided.
        - Extract the field being updated.
        - Extract its new value.
        - Valid fields are name, description, and due_date.
        - Do not invent missing information.

        For delete_task:
        - Extract task_id if explicitly provided.
        - Otherwise, extract the task name if provided.
        - Do not guess task identifiers.

        For view_tasks:
        - Extract status if the user requests a specific status.
        - Valid status filters are Pending, Completed, and Overdue.
        - If the user requests overdue tasks, return "Overdue".
        - Never interpret viewing completed tasks as a command to complete tasks.
        - If the user requests all tasks, status must be null.
        - Do not confuse status filtering with task completion.
        
        For complete_task:
        - Extract task_id if explicitly provided.
        - Otherwise, extract the task name if provided.
        - Extract either task_id or name, not both,
        unless the user explicitly provides both.
        - Do not extract unrelated task details.
        - Do not invent task identifiers or names.
        - Do not allow the user to set arbitrary status values.
        - The task must be identified before it can be completed.
        - Do not extract status from the user's message.
        - The Python application will handle the status update.

        IMPORTANT RULES:
        - Understand different natural-language expressions.
        - Do not confuse task names with task IDs.
        - Task IDs must be integers.
        - Return null for missing information.
        - Do not invent dates or other information.
        - Return only valid JSON.
        
        CURRENT DATE:
            {current_date}

            DATE EXTRACTION RULES:
            - Interpret relative dates using the CURRENT DATE above.
            - "today" means the current date.
            - "tomorrow" means the next calendar date.
            - "yesterday" means the previous calendar date.
            - Convert relative dates into YYYY-MM-DD format.
            - For dates such as "next Monday", calculate the correct calendar date.
            - If the user doesn't mention a due date, return null.
            - Never guess a date.

        OUTPUT FORMAT:

        {{
            "intent": "intent_name",
            "entities": {{
                "task_id": null,
                "name": null,
                "description": null,
                "due_date": null,
                "field": null,
                "new_value": null,
                "status": null
            }}
        }}

        USER MESSAGE:
        {user_input}
        """
    
    
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents= analysis_prompt,
            config = {
                "response_mime_type": "application/json"
            }
    )
        result = json.loads(response.text)
        print(type(result))
        return result
    
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None

    except errors.ClientError as e:
        print(f"Client error: {e}")
        return None

    except errors.ServerError as e:
        print(f"Server error: {e}")
        return None

    except errors.APIError as e:
        print(f"API error: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    
    