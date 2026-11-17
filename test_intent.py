from gemini_client import analyze_user_prompt

user_input = "delete task 1"

result = analyze_user_prompt(user_input)


print(result)
print(type(result))