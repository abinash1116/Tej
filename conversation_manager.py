import json
import os

History_file = os.path.join(os.path.dirname(__file__), "conversation_history.json")

def load_conversation_history():
    if not os.path.exists(History_file):
        return []
    with open(History_file, "r") as file:
        return json.load(file)
    
def save_conversation_history(history):
    with open(History_file, "w") as file:
        json.dump(history, file, indent = 4)

def add_message(history, role, content):
    
    message = {
        "role": role,
        "content": content
    }
    
    history.append(message)
    save_conversation_history(history)
        