from gemini_client import generate_response

print("Tej is connecting to Gemini...")

prompt = input("Enter your prompt: ")
response = generate_response(prompt)

print("\nTej Says: ")
print(response)