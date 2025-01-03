# Generative AI PC Automation example
A simple example of how to automate pc with generative ai.

## PyAutoGUI_generator.py
This script uses OpenAI's GPT-4o model to generate PyAutoGUI code based on user prompts.  
It allows users to describe actions they want to automate on their computer, and the script generates the corresponding PyAutoGUI code to perform those actions.

### Requirements
- Python 3.10 or higher
- OpenAI API key

### Installation
Install the required libraries:
```
pip install openai pyautogui python-dotenv
```

### Usage
1. Put your OpenAI API key in the [.env file](https://pypi.org/project/python-dotenv/).
2. Run the script.
3. Enter your prompt when prompted.
4. The script will generate the PyAutoGUI code and let you review it before executing.
5. WARNING: execute code only after careful review to avoid unintended actions.