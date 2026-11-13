from gemini_client import generate_response
from conversation_manager import load_conversation_history, add_message

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
        
        response = generate_response(user_input, history)
        if response is None:
            print("Sorry, I couldn't generate a response. Please try again.")
            continue
        else:
            add_message(history, "user", user_input)
            add_message(history, "model", response)
            print("\nTej: ",response)
            print()
        
if __name__ == "__main__":
    start_assistant()