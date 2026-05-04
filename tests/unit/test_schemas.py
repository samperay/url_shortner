import pytest
from pydantic import ValidationError

from app.schemas import URLCreate, URLResponse


def test_url_create_accepts_valid_http_url():
    payload = URLCreate(original_url="https://example.com/articles?id=123")

    assert str(payload.original_url) == "https://example.com/articles?id=123"


def test_url_create_rejects_invalid_url():
    with pytest.raises(ValidationError):
        URLCreate(original_url="not-a-url")


def test_url_response_serializes_original_and_short_urls():
    response = URLResponse(
        original_url="https://example.com/original",
        short_url="http://testserver/abc123",
    )

    assert response.model_dump() == {
        "original_url": "https://example.com/original",
        "short_url": "http://testserver/abc123",
    }
