from google import genai
import os
from dotenv import load_dotenv

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
        model = "gemini-3.5-flash-lite",
        contents = contents
    )
    
    return response.text