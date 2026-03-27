from src.state import IAVCGraphState
from src.nodes import validate_article, chunk_article

def test_validate_article_success():
    state: IAVCGraphState = {
        "article_content": "This is a sufficiently long article content used for testing the validation logic. We need at least 50 characters here to pass.",
        "article_title": "Test Title"
    }
    result = validate_article(state)
    assert result["validation_status"] == "success"

def test_validate_article_failure_short():
    state: IAVCGraphState = {
        "article_content": "Too short",
        "article_title": "Test Title"
    }
    result = validate_article(state)
    assert result["validation_status"] == "failed"
    assert "error_message" in result

def test_chunk_article():
    state: IAVCGraphState = {
        "article_content": "A" * 600,
        "article_url": "http://test.com",
        "article_title": "Test Title",
        "article_category": "Test"
    }
    result = chunk_article(state)
    chunks = result["chunks"]
    assert len(chunks) == 2
    assert len(chunks[0]["text"]) == 500
    assert len(chunks[1]["text"]) == 150 # 600 total, overlap 50 -> 0-500, then 450-600 (len = 150)
