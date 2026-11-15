from google import genai
import os
from dotenv import load_dotenv
from google.genai import errors
import json
import traceback

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

        6. unknown:
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
        - No entities are required.

        IMPORTANT RULES:
        - Understand different natural-language expressions.
        - Do not confuse task names with task IDs.
        - Task IDs must be integers.
        - Return null for missing information.
        - Do not invent dates or other information.
        - Return only valid JSON.

        OUTPUT FORMAT:

        {{
            "intent": "intent_name",
            "entities": {{
                "task_id": null,
                "name": null,
                "description": null,
                "due_date": null,
                "field": null,
                "new_value": null
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

    
    