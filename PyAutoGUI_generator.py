from openai import OpenAI
from dotenv import load_dotenv
import sys
import json
import pyautogui
import os
import subprocess

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def call_openai_api(user_prompt, previous_code=None, error_info=None):
    if previous_code and error_info:
        prompt = f"""Fix this PyAutoGUI code for {sys.platform}:
                     Previous code:
                     {previous_code}

                     Error received:
                     {error_info}

                     Original task: 
                     {user_prompt}"""
    else:
        prompt = f"Write PyAutoGUI code to {user_prompt} on {sys.platform}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are a skilled Python developer and automation expert. 
                 Return valid Python (PyAutoGUI) code as JSON that can be executed through the exec().
                 Never assume, use code or web search to get actual data."""},
                {"role": "user", "content": f"Return the following as JSON: {prompt}"}
            ],
            response_format={ "type": "json_object" },
            functions=[{
                "name": "provide_code",
                "description": "Provide PyAutoGUI code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute"
                            }
                        },
                        "required": ["code"]
                    }
                }],
            function_call={"name": "provide_code"})
        return json.loads(response.choices[0].message.function_call.arguments)["code"]
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def main():
    while True:
        retry_count = 0
        print("Enter your task prompt (e.g., 'use the calculator to increase current year by 10 and print the result to terminal'): ")
        user_prompt = input().strip()
        
        if not user_prompt:
            print("Invalid input. Please provide a task prompt.")
            continue

        print("Generating code...")
        extracted_code = call_openai_api(user_prompt)

        while retry_count < 5:

            if not extracted_code:
                print("Failed to generate a response. Please try again.")
                break

            print("Here is the code generated for your prompt:")
            print(extracted_code)

            print("Would you like to execute this code (yes(y) / no(n)) or modify the prompt (modify(m))?")
            user_decision = input().strip().lower()

            if user_decision == "yes" or user_decision == "y":
                try:
                    print("Executing the code...")
                    exec(extracted_code, globals())
                    print("Execution complete.")
                    return
                except Exception as e:
                    retry_count += 1;
                    error_info = str(e)
                    print(f"Error during execution: {error_info}")
                    if retry_count < 5:
                        print(f"Retrying with error information... (attempt {retry_count}/5)")
                        extracted_code = call_openai_api(user_prompt, extracted_code, error_info)
                    else:
                        print("Maximum retry attempts reached. Please try a different prompt.")
                        break
            elif user_decision == "modify" or user_decision == "m":
                print("Enter a new task prompt.")
                break
            elif user_decision == "no" or user_decision == "n":
                print("Terminating program. Goodbye!")
                sys.exit() 
            else:
                print("Invalid input. Please enter 'yes(y)', 'no(n)', or 'modify(m)'.")

if __name__ == "__main__":
    main()