import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from dotenv import load_dotenv

load_dotenv()

LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "MBZUAI/LaMini-Flan-T5-783M")

explain_tokenizer = None
explain_model = None
_model_load_attempted = False

def get_model_and_tokenizer():
    """Lazily load the tokenizer and model for explanations."""
    global explain_tokenizer, explain_model, _model_load_attempted
    if explain_tokenizer is not None and explain_model is not None:
        return explain_tokenizer, explain_model

    if _model_load_attempted and explain_model is None:
        return None, None

    _model_load_attempted = True
    try:
        cache_dir = os.getenv("HF_HOME", "D:/.hf_cache")
        print(f"Loading local model '{LOCAL_MODEL_NAME}' from cache: {cache_dir}...")
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME, cache_dir=cache_dir)
        model = AutoModelForSeq2SeqLM.from_pretrained(LOCAL_MODEL_NAME, cache_dir=cache_dir)
        device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        model = model.to(device)
        explain_tokenizer = tokenizer
        explain_model = model
        print("Local model loaded successfully.")
        return explain_tokenizer, explain_model
    except Exception as e:
        print(f"Warning: Could not load local model '{LOCAL_MODEL_NAME}': {e}")
        return None, None

def explain_topic(topic: str) -> str:
    """
    Explains the concept of the given topic in a simple and clear way for a school student.
    Uses MBZUAI/LaMini-Flan-T5-783M locally, with seamless fallback if local model is downloading or unavailable.
    """
    if not topic or not topic.strip():
        return "Please provide a valid topic to explain."

    tokenizer, model = get_model_and_tokenizer()

    if tokenizer is not None and model is not None:
        try:
            input_text = f"Explain the concept of '{topic.strip()}' in a simple and clear way for a school student."
            device = next(model.parameters()).device
            inputs = tokenizer(input_text, return_tensors="pt").to(device)

            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                do_sample=True
            )

            explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return explanation
        except Exception as e:
            print(f"Local inference error: {e}")

    # Fallback via Gemini if local model is offline/unavailable
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
            gemini_model = genai.GenerativeModel(model_name=model_name)
            response = gemini_model.generate_content(
                f"Explain the concept of '{topic.strip()}' in a simple and clear way for a school student. Keep it concise, clear, and beginner-friendly."
            )
            return response.text.strip()
    except Exception as genai_err:
        print(f"Fallback generation error: {genai_err}")

    return f"⚠️ Could not generate explanation for '{topic}'. Ensure local model files are downloaded or GEMINI_API_KEY is configured in .env."
