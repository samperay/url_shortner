from app.models import URLMapping
from app.repositories import URLRepository


def test_create_url_mapping_persists_mapping(db_session):
    repository = URLRepository()

    mapping = repository.create_url_mapping(
        db=db_session,
        original_url="https://example.com/articles/fastapi",
        short_code="abc123",
    )

    assert mapping.id is not None
    assert mapping.original_url == "https://example.com/articles/fastapi"
    assert mapping.short_code == "abc123"
    assert mapping.created_at is not None
    assert db_session.query(URLMapping).count() == 1


def test_get_by_short_code_returns_matching_mapping(db_session):
    repository = URLRepository()
    repository.create_url_mapping(
        db=db_session,
        original_url="https://example.com/a",
        short_code="codeA",
    )

    mapping = repository.get_by_short_code(db=db_session, short_code="codeA")

    assert mapping is not None
    assert mapping.original_url == "https://example.com/a"


def test_get_by_original_url_returns_matching_mapping(db_session):
    repository = URLRepository()
    repository.create_url_mapping(
        db=db_session,
        original_url="https://example.com/original",
        short_code="orig01",
    )

    mapping = repository.get_by_original_url(
        db=db_session,
        original_url="https://example.com/original",
    )

    assert mapping is not None
    assert mapping.short_code == "orig01"
