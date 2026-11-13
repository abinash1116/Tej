from google import genai
import os
from dotenv import load_dotenv
from google.genai import errors

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
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents
    )
        return response.text
    
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