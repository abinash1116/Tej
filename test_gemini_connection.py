from google import genai
import os
from dotenv import load_dotenv

print("TEJ Gemini test started!")
load_dotenv()
api_key = os.getenv("Gemini_API_Key")

if not api_key:
    print("API not found")
    exit()

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model = "gemini-flash-latest",
    contents = "Hello Gemini introduce yourself briefly."
)

print("\n Gemini Says:")
print(response.text)

client.close()