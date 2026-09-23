import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=api_key)

def answer_question_with_gemini(question: str) -> str:
    """Answers an academic or general inquiry using Google Gemini."""
    if not question or not question.strip():
        return "Please provide a valid question."
    try:
        current_key = os.getenv("GEMINI_API_KEY")
        if not current_key or current_key == "YOUR_GEMINI_API_KEY_HERE":
            return "⚠️ Gemini API key is missing. Please set GEMINI_API_KEY in your .env file."

        genai.configure(api_key=current_key)
        model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
        # Ensure prefix format compatibility
        if not model_name.startswith("models/") and not model_name.startswith("gemini-"):
            model_name = f"models/{model_name}"
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(question.strip())
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error in QnA: {e}"
