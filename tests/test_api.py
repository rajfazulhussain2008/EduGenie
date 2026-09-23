import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_home_page():
    """Verify that the home page loads with HTTP 200 and expected markup."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to EduGenie" in response.text
    assert "Ask EduGenie a Question" in response.text
    assert "Need an Explanation?" in response.text
    assert "Generate an Interactive Quiz" in response.text

def test_health_check():
    """Verify health check endpoint returns 200 and status metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "gemini_configured" in data
    assert "local_model" in data

def test_qa_validation_error():
    """Verify that an empty or missing question query parameter returns 422 or 400."""
    response = client.get("/qa?question=")
    assert response.status_code in [400, 422]

@patch("main.answer_question_with_gemini")
def test_qa_success(mock_qa):
    """Verify /qa route dispatches correctly to answering logic."""
    mock_qa.return_value = "The Pacific Ocean is the largest ocean on Earth."
    response = client.get("/qa?question=Which+is+the+largest+ocean?")
    assert response.status_code == 200
    assert response.json() == {"answer": "The Pacific Ocean is the largest ocean on Earth."}
    mock_qa.assert_called_once_with("Which is the largest ocean?")

def test_explain_validation_error():
    """Verify that missing topic in /explain returns 400."""
    response = client.post("/explain/", json={})
    assert response.status_code == 400
    assert "error" in response.json()

@patch("main.explain_topic")
def test_explain_success(mock_explain):
    """Verify /explain/ returns explanation correctly."""
    mock_explain.return_value = "Photosynthesis is how plants make food using sunlight."
    response = client.post("/explain/", json={"topic": "Photosynthesis"})
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Photosynthesis"
    assert data["explanation"] == "Photosynthesis is how plants make food using sunlight."

def test_summarize_validation_error():
    """Verify that missing text in /summarize returns 400."""
    response = client.post("/summarize/", json={})
    assert response.status_code == 400

@patch("main.summarize_text")
def test_summarize_success(mock_summarize):
    """Verify /summarize/ returns condensed summary."""
    mock_summarize.return_value = "The Industrial Revolution shifted farming to factories."
    response = client.post("/summarize/", json={"text": "Long historical text..."})
    assert response.status_code == 200
    assert response.json() == {"summary": "The Industrial Revolution shifted farming to factories."}

def test_quiz_validation_error():
    """Verify that missing text in /quiz returns 400."""
    response = client.post("/quiz", json={})
    assert response.status_code == 400

@patch("main.generate_quiz")
def test_quiz_success(mock_quiz):
    """Verify /quiz returns structured list of MCQs."""
    mock_quiz.return_value = [
        {
            "question": "What is the powerhouse of the cell?",
            "options": ["Mitochondria", "Nucleus", "Ribosome", "Chloroplast"],
            "answer": "Mitochondria"
        }
    ]
    response = client.post("/quiz", json={"text": "Cell biology"})
    assert response.status_code == 200
    assert "quiz" in response.json()
    assert len(response.json()["quiz"]) == 1
    assert response.json()["quiz"][0]["answer"] == "Mitochondria"

def test_learning_recommendations_validation_error():
    """Verify missing topic in /learn/recommendations returns 400 or 422."""
    response = client.get("/learn/recommendations?topic=")
    assert response.status_code in [400, 422]

@patch("main.get_learning_recommendations")
def test_learning_recommendations_success(mock_recs):
    """Verify /learn/recommendations returns personalized path."""
    mock_recs.return_value = "## SQL Learning Roadmap: 1. SELECT 2. JOIN 3. INDEX"
    response = client.get("/learn/recommendations?topic=SQL")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "SQL"
    assert "SQL Learning Roadmap" in data["recommendation"]
