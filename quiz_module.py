import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=api_key)

def clean_json_block(text: str) -> str:
    """Removes Markdown ```json code fences and extra spaces."""
    cleaned = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL).strip()
    return cleaned

def generate_quiz(text: str) -> list:
    """
    Generates 3 multiple-choice questions (MCQs) from a given passage or topic.
    Returns a Python list of question objects with question, options, and answer.
    """
    if not text or not text.strip():
        return [{"error": "Please provide text or a topic to generate a quiz."}]

    try:
        current_key = os.getenv("GEMINI_API_KEY")
        if not current_key or current_key == "YOUR_GEMINI_API_KEY_HERE":
            return [{"error": "Gemini API key is not configured. Please set GEMINI_API_KEY in .env"}]

        genai.configure(api_key=current_key)
        model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
        if not model_name.startswith("models/") and not model_name.startswith("gemini-"):
            model_name = f"models/{model_name}"

        model = genai.GenerativeModel(model_name=model_name)

        prompt = f"""
You are a quiz generator.

From the following passage, create 3 multiple-choice questions. Each question should include:
- A "question"
- A list of 4 "options"
- A correct "answer" that must exactly match one of the options.

Format your output as **valid JSON**, like this:
[
  {{
    "question": "What is ...?",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Passage:
{text.strip()}
"""
        response = model.generate_content(prompt)
        quiz_text = response.text.strip()

        # Clean markdown code blocks if any
        cleaned_text = clean_json_block(quiz_text)

        # Extract JSON array if surrounded by conversational filler
        match = re.search(r"\[\s*\{.*\}\s*\]", cleaned_text, re.DOTALL)
        if match:
            cleaned_text = match.group(0)

        parsed = json.loads(cleaned_text)
        if isinstance(parsed, list):
            return parsed
        return [{"error": "Quiz output could not be parsed into a list."}]
    except Exception as e:
        return [{"error": f"Failed to generate quiz: {str(e)}"}]
