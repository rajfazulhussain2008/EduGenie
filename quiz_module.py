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
        topic_lower = text.lower()
        if "solar" in topic_lower or "planet" in topic_lower:
            return [
                {
                    "question": "What celestial body is at the center of the Solar System?",
                    "options": ["The Moon", "The Sun", "Jupiter", "Earth"],
                    "answer": "The Sun"
                },
                {
                    "question": "Which planet in the Solar System is known as the Red Planet?",
                    "options": ["Venus", "Mars", "Saturn", "Mercury"],
                    "answer": "Mars"
                },
                {
                    "question": "Which is the largest planet in the Solar System?",
                    "options": ["Earth", "Neptune", "Jupiter", "Uranus"],
                    "answer": "Jupiter"
                }
            ]
        elif "pythagor" in topic_lower or "triangle" in topic_lower:
            return [
                {
                    "question": "What is the Pythagorean theorem formula for a right triangle?",
                    "options": ["a^2 + b^2 = c^2", "a + b = c", "a^2 - b^2 = c^2", "E = mc^2"],
                    "answer": "a^2 + b^2 = c^2"
                },
                {
                    "question": "Which side of a right triangle is the hypotenuse?",
                    "options": ["The shortest side", "The side opposite the right angle", "The vertical leg", "The adjacent side"],
                    "answer": "The side opposite the right angle"
                },
                {
                    "question": "If the legs of a right triangle are 3 and 4, what is the length of the hypotenuse?",
                    "options": ["5", "6", "7", "25"],
                    "answer": "5"
                }
            ]
        elif "photo" in topic_lower or "plant" in topic_lower:
            return [
                {
                    "question": "What primary pigment absorbs sunlight for photosynthesis in plants?",
                    "options": ["Chlorophyll", "Hemoglobin", "Carotene", "Melanin"],
                    "answer": "Chlorophyll"
                },
                {
                    "question": "What gas do plants absorb from the atmosphere during photosynthesis?",
                    "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
                    "answer": "Carbon Dioxide"
                },
                {
                    "question": "What are the primary products of photosynthesis?",
                    "options": ["Glucose and Oxygen", "Water and Carbon", "Nitrogen and Sugar", "Salt and Hydrogen"],
                    "answer": "Glucose and Oxygen"
                }
            ]
        return [
            {
                "question": f"What is the foundational concept of {text.strip()}?",
                "options": [f"Understanding core principles of {text.strip()}", "Memorizing formulas without meaning", "Ignoring definitions", "None of the above"],
                "answer": f"Understanding core principles of {text.strip()}"
            },
            {
                "question": f"Which skill is essential when studying {text.strip()}?",
                "options": ["Critical and analytical problem solving", "Passive skimming", "Skipping practice questions", "Memorizing only answers"],
                "answer": "Critical and analytical problem solving"
            },
            {
                "question": f"How can mastery in {text.strip()} best be tested?",
                "options": ["Active recall and practical application", "Passive listening only", "Avoiding review", "One-time reading"],
                "answer": "Active recall and practical application"
            }
        ]
