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

def call_openai_api(user_prompt):
    prompt = f"Write PyAutoGUI code to {user_prompt} on {sys.platform}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled Python developer. Return valid Python code as JSON that can be executed."},
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
        # Step 1: Prompt user for input
        print("Enter your task prompt (e.g., 'use the calculator to multiply 2*3'): ")
        user_prompt = input().strip()

        if not user_prompt:
            print("Invalid input. Please provide a task prompt.")
            continue

        # Step 2: Call the OpenAI API
        print("Generating code...")
        extracted_code = call_openai_api(user_prompt)

        if not extracted_code:
            print("Failed to generate a response. Please try again.")
            continue

        # Step 3: Display the generated code
        print("Here is the code generated for your prompt:")
        print(extracted_code)

        # Step 4: Ask the user how to proceed
        print("Would you like to execute this code (yes/no) or modify the prompt (modify)?")
        user_decision = input().strip().lower()

        if user_decision == "yes":
            try:
                print("Executing the code...")
                exec(extracted_code)
                print("Execution complete.")
                break
            except Exception as e:
                print(f"Error during execution: {e}")
                print("Returning to prompt for correction.")
        elif user_decision == "modify":
            print("Enter a new task prompt.")
            continue
        elif user_decision == "no":
            print("Terminating program. Goodbye!")
            break
        else:
            print("Invalid input. Please enter 'yes', 'no', or 'modify'.")

if __name__ == "__main__":
    main()
