import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=api_key)

def summarize_text(text: str) -> str:
    """
    Summarizes long educational passages into concise, clear revision summaries
    retaining core information and key takeaways.
    """
    if not text or not text.strip():
        return "Please provide text to summarize."

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
You are an expert educational summarizer.
Condense the following educational passage into a concise, easy-to-understand summary ideal for quick student revision.
Retain core concepts, key facts, and takeaways while eliminating redundancy.

Passage:
{text.strip()}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error in summarization: {e}"
