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
                {"role": "system", "content": "You are a skilled Python developer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def extract_code_from_response(response):
    try:
        # Assuming the code block is enclosed in triple backticks
        start = response.find("```python") + len("```python")
        end = response.find("```", start)
        return response[start:end].strip()
    except Exception as e:
        print(f"Error extracting code: {e}")
        return None

def main():
    while True:
        # Step 1: Prompt user for input
        print("v2 Enter your task prompt (e.g., 'use the calculator to multiply 2*3'): ")
        user_prompt = input().strip()

        if not user_prompt:
            print("Invalid input. Please provide a task prompt.")
            continue

        # Step 2: Call the OpenAI API
        print("Generating code...")
        api_response = call_openai_api(user_prompt)

        if not api_response:
            print("Failed to generate a response. Please try again.")
            continue

        # Step 3: Extract code block from API response
        extracted_code = extract_code_from_response(api_response)

        if not extracted_code:
            print("Failed to extract code from response. Please try again.")
            continue

        # Step 4: Display the generated code
        print("Here is the code generated for your prompt:")
        print(extracted_code)

        # Step 5: Ask the user how to proceed
        print("Would you like to execute this code (yes/no) or modify the prompt (modify)?")
        user_decision = input().strip().lower()

        if user_decision == "yes":
            # Step 6.a: Execute the code
            try:
                print("Executing the code...")
                exec(extracted_code)
                print("Execution complete.")
                break
            except Exception as e:
                print(f"Error during execution: {e}")
                print("Returning to prompt for correction.")
        elif user_decision == "modify":
            # Step 6.b: Modify the prompt
            print("Enter a new task prompt.")
            continue
        elif user_decision == "no":
            print("Terminating program. Goodbye!")
            break
        else:
            print("Invalid input. Please enter 'yes', 'no', or 'modify'.")

if __name__ == "__main__":
    main()
