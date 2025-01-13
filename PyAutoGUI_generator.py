from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import sys
import json
import os

MAX_RETRY_ATTEMPTS = 5
MODEL_NAME = "gpt-4o"
SYSTEM_PROMPT = """You are a skilled Python developer and automation expert. 
                   Return valid Python (PyAutoGUI) code as JSON that can be executed through the exec().
                   Never assume, use code or web search to get actual data."""
API_FUNCTION_SCHEMA = {
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
}

class PyAutoGUIGenerator:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.retry_count = 0

    def generate_code(self, user_prompt, previous_code=None, error_info=None):
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
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Return the following as JSON: {prompt}"}
                ],
                response_format={ "type": "json_object" },
                functions=[API_FUNCTION_SCHEMA],
                function_call={"name": "provide_code"})
            return json.loads(response.choices[0].message.function_call.arguments)["code"]
        except OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def execute_code(self, code):
        try:
            print("Executing the code...")
            restricted_globals = {
                '__builtins__': __builtins__
            }
            exec(code, restricted_globals)
            print("Execution complete.")
            return True
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            return False

    def run(self):
        while True:
            retry_count = 0
            user_prompt = UserInterface.get_user_prompt()
            
            if not user_prompt:
                print("Invalid input. Please provide a task prompt.")
                continue

            print("Generating code...")
            extracted_code = self.generate_code(user_prompt)

            while retry_count < MAX_RETRY_ATTEMPTS:

                if not extracted_code:
                    print("Failed to generate a response. Please try again.")
                    break

                print("Here is the code generated for your prompt:")
                print(extracted_code)

                user_decision = UserInterface.get_user_decision()

                if user_decision == "execute":
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
                            extracted_code = self.generate_code(user_prompt, extracted_code, error_info)
                        else:
                            print("Maximum retry attempts reached. Please try a different prompt.")
                            break
                elif user_decision == "modify":
                    print("Enter a new task prompt.")
                    break
                elif user_decision == "retry":
                    print("Regenerating code with the same prompt...")
                    retry_count = 0  # Reset retry count for the new attempt
                    extracted_code = self.generate_code(user_prompt)
                    continue
                elif user_decision == "exit":
                    print("Terminating program. Goodbye!")
                    sys.exit(1)
            pass
    
class UserInterface:
    @staticmethod
    def get_user_prompt():
        while True:
            print("Enter your task prompt (e.g., 'use the calculator to increase current year by 10 and print the result to terminal'): ")
            prompt = input().strip()
            if prompt:
                return prompt
            print("Invalid input. Please provide a task prompt.")

    @staticmethod
    def get_user_decision():
        valid_responses = {
            ('yes', 'y'): 'execute',
            ('no', 'n'): 'exit',
            ('modify', 'm'): 'modify',
            ('retry', 'r'): 'retry'
        }
        while True:
            print("Would you like to execute this code (y / n), modify the prompt (m), or retry with same prompt (r)?")
            response = input().strip().lower()
            for keys, value in valid_responses.items():
                if response in keys:
                    return value
            print("Invalid input. Please enter 'yes(y)', 'no(n)', 'modify(m)', or 'retry(r)'.")

def main():
    generator = PyAutoGUIGenerator()
    
    try:
        generator.run()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()