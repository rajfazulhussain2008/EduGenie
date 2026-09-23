# EduGenie 🧠✨ — AI-Powered Learning Assistant

EduGenie is a full-stack, production-ready educational assistant engineered to simplify and accelerate learning for students and independent learners. It combines cloud-based reasoning via **Google Gemini 1.5 Pro** with an offline-capable, lightweight local language model (**`MBZUAI/LaMini-Flan-T5-783M`**) running on PyTorch and Hugging Face Transformers.

---

## 🌟 Key Features

1. **💡 Smart Academic Q&A (`/qa`)**
   - Instant, accurate answers to academic and general knowledge questions powered by Google Gemini 1.5 Pro.
2. **🔬 Concept Explainer (`/explain/`)**
   - Breaks down complex scientific, mathematical, or humanities topics into clear, intuitive explanations tuned for school students using the local instruction-tuned `LaMini-Flan-T5-783M` model (with cloud fallback).
3. **📝 Paragraph Summarizer (`/summarize/`)**
   - Condenses lengthy textbook chapters, historical passages, and lecture notes into high-yield study summaries.
4. **🎯 Interactive Self-Assessment Quiz (`/quiz`)**
   - Generates 3 contextual multiple-choice questions (MCQs) with 4 plausible options each, complete with real-time answer verification, feedback, and score calculation.
5. **🗺️ Adaptive Learning Roadmap (`/learn/recommendations`)**
   - Provides personalized step-by-step learning paths structured across Beginner, Intermediate, and Advanced tiers, complete with recommended books, articles, and video resources.

---

## 🏗️ Architecture

```
                    ┌────────────────────────┐
                    │  Student / Web Browser │
                    └───────────┬────────────┘
                                │ HTTP / JSON
                                ▼
                    ┌────────────────────────┐
                    │   FastAPI App Server   │
                    │   (main.py / app.py)   │
                    └─────┬────────────┬─────┘
                          │            │
       Cloud REST API     │            │  In-Memory / Local PyTorch
      (google-genai)      ▼            ▼  (Hugging Face Transformers)
                 ┌──────────────┐   ┌──────────────────────────┐
                 │ Google Gemini│   │  MBZUAI/LaMini-Flan-T5   │
                 │   1.5 Pro    │   │           783M           │
                 └──────────────┘   └──────────────────────────┘
```

---

## 📁 Project Structure

```
Edu Genie/
├── static/
│   ├── style.css                 # Polished, responsive glassmorphism UI styles
│   └── script.js                 # Interactive quiz engine, async API calls & markdown parser
├── templates/
│   └── index.html                # Jinja2 template with hero header and module dashboard
├── tests/
│   ├── test_api.py               # Integration tests for all endpoints and schemas
│   └── test_modules.py           # Unit tests for prompt cleaning, validation, and parsing
├── app.py                        # Epic 3 entrypoint alias (`uvicorn app:app`)
├── main.py                       # Core FastAPI application (`uvicorn main:app`)
├── explanation_module.py         # Local transformer concept explanation logic
├── qna.py                        # Gemini question-answering module
├── quiz_module.py                # MCQ quiz generation and JSON fence stripping
├── summary_module.py             # Passage summarization module
├── learning_path.py              # Multi-tier curriculum and roadmap generator
├── requirements.txt              # Production dependency specifications
├── .env                          # Local environment variables and API keys
├── .gitignore                    # Git tracking rules
└── README.md                     # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python**: 3.10+ installed and added to `PATH`.
- **Git**: Installed for version control.
- **Google Gemini API Key**: Obtain a free key from [Google AI Studio](https://aistudio.google.com/).

### 2. Configure Environment Variables
Open the `.env` file in the project root and add your Gemini API Key:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
LOCAL_MODEL_NAME=MBZUAI/LaMini-Flan-T5-783M
HOST=127.0.0.1
PORT=8000
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application Server
You can launch EduGenie using either the documented `main:app` or `app:app` commands:

```bash
uvicorn main:app --reload
```
*Or:*
```bash
uvicorn app:app --reload
```

Once started, open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Running Automated Tests

Run the test suite with `pytest`:
```bash
python -m pytest tests/ -v
```

All integration tests for `/qa`, `/explain/`, `/summarize/`, `/quiz`, `/learn/recommendations`, and health check routes will execute.

---

## 📡 API Reference

| Endpoint | Method | Input | Description |
| :--- | :---: | :--- | :--- |
| `/` | `GET` | — | Serves the web dashboard interface |
| `/qa` | `GET` | `?question=...` | Answers general and academic questions |
| `/explain/` | `POST` | `{"topic": "..."}` | Explains a concept in simple student terms |
| `/summarize/` | `POST` | `{"text": "..."}` | Condenses text into revision notes |
| `/quiz` | `POST` | `{"text": "..."}` | Generates 3 MCQs with options and answer |
| `/learn/recommendations` | `GET` | `?topic=...` | Generates structured learning roadmap |
| `/health` | `GET` | — | System and API configuration status check |

---

## 🎓 Authors & Mentors
* **Author**: Tella Divya Sree
* **Mentor**: Siri
* **Framework**: FastAPI, Google Gemini, Hugging Face Transformers
