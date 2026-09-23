import pytest
from quiz_module import clean_json_block, generate_quiz
from qna import answer_question_with_gemini
from summary_module import summarize_text
from learning_path import get_learning_recommendations

def test_clean_json_block():
    """Test stripping markdown code fences."""
    raw = '```json\n[{"question": "Q1", "options": ["A","B","C","D"], "answer": "A"}]\n```'
    cleaned = clean_json_block(raw)
    assert cleaned == '[{"question": "Q1", "options": ["A","B","C","D"], "answer": "A"}]'

def test_clean_json_block_no_fence():
    """Test string without code fences remains clean."""
    raw = '{"key": "value"}'
    assert clean_json_block(raw) == '{"key": "value"}'

def test_empty_inputs():
    """Test safe handling when given empty or whitespace inputs."""
    assert "valid question" in answer_question_with_gemini("").lower()
    assert "provide text" in summarize_text("   ").lower()
    assert "provide a topic" in get_learning_recommendations("").lower()
    quiz_res = generate_quiz("")
    assert "error" in quiz_res[0]
