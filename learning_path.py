import os
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=api_key)

def get_learning_recommendations(topic: str) -> str:
    """
    Generates a personalized, structured, and adaptive learning path for a given topic,
    spanning Beginner, Intermediate, and Advanced stages, complete with recommended resources.
    """
    if not topic or not topic.strip():
        return "Please provide a topic to generate learning recommendations."

    try:
        current_key = os.getenv("GEMINI_API_KEY")
        if not current_key or current_key == "YOUR_GEMINI_API_KEY_HERE":
            return "⚠️ Gemini API key is missing. Please set GEMINI_API_KEY in your .env file."

        genai.configure(api_key=current_key)
        model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
        if not model_name.startswith("models/") and not model_name.startswith("gemini-"):
            model_name = f"models/{model_name}"

        model = genai.GenerativeModel(model_name=model_name)

        prompt = f"""
You are an AI tutor. The student wants to learn about: {topic.strip()}.
Suggest a structured and adaptive learning path including key topics, order of learning, and resources (books, videos, articles).
Include beginner, intermediate, and advanced levels if needed.
"""
        response = model.generate_content(prompt)
        print("🧠 Gemini raw response:", response)

        if hasattr(response, "text") and response.text:
            return response.text.strip()
        elif hasattr(response, "parts") and response.parts:
            return response.parts[0].text.strip()
        else:
            return "❌ Could not extract content from Gemini response."
    except Exception as e:
        traceback.print_exc()
        return f"❌ Error occurred: {str(e)}"
