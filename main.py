import os
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import EduGenie core modules
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz
from learning_path import get_learning_recommendations

load_dotenv()

app = FastAPI(
    title="EduGenie",
    description="Google Gemini & Local Model-Powered Learning Assistant",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and Templates setup
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Root endpoint - serves UI
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    response = templates.TemplateResponse(request=request, name="index.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Q&A - GET API using Gemini
@app.get("/qa")
async def answer_question(question: str = Query(..., description="Academic or general question")):
    if not question or not question.strip():
        return JSONResponse(content={"error": "Please provide a valid question."}, status_code=400)
    answer = answer_question_with_gemini(question)
    return {"answer": answer}

# Explanation - POST API using Local Model (with cloud fallback)
@app.post("/explain")
@app.post("/explain/")
async def explain_api(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

    topic = data.get("topic")
    if not topic or not str(topic).strip():
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)

    explanation = explain_topic(topic)
    return {"topic": topic, "explanation": explanation}

# Summarization - POST API using Gemini
@app.post("/summarize")
@app.post("/summarize/")
async def summarize_api(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

    text = data.get("text")
    if not text or not str(text).strip():
        return JSONResponse(content={"error": "Please provide text to summarize."}, status_code=400)

    summary = summarize_text(text)
    return {"summary": summary}

# Quiz Generation - POST API using Gemini
@app.post("/quiz")
@app.post("/quiz/")
async def quiz_api(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

    text = data.get("text")
    if not text or not str(text).strip():
        return JSONResponse(content={"error": "Please provide text for quiz."}, status_code=400)

    quiz = generate_quiz(text)
    print("Generated quiz:", quiz)  # Debug trace
    return JSONResponse(content={"quiz": quiz})

# Learning Recommendations - GET API using Gemini
@app.get("/learn/recommendations")
async def learning_recommendation_api(topic: str = Query(..., description="Topic to generate learning path for")):
    if not topic or not topic.strip():
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)

    recommendation = get_learning_recommendations(topic)
    return {"topic": topic, "recommendation": recommendation}

# System Health Check
@app.get("/health")
async def health_check():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    key_configured = bool(gemini_key and gemini_key != "YOUR_GEMINI_API_KEY_HERE")
    return {
        "status": "online",
        "gemini_configured": key_configured,
        "local_model": os.getenv("LOCAL_MODEL_NAME", "MBZUAI/LaMini-Flan-T5-783M")
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
