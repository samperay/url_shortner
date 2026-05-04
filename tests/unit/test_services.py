from types import SimpleNamespace

from app.services import URLShortenerService


class FakeRepository:
    def __init__(self, original_url_result=None, short_code_results=None):
        self.original_url_result = original_url_result
        self.short_code_results = list(short_code_results or [])
        self.created = []

    def get_by_original_url(self, db, original_url):
        return self.original_url_result

    def get_by_short_code(self, db, short_code):
        if self.short_code_results:
            return self.short_code_results.pop(0)
        return None

    def create_url_mapping(self, db, original_url, short_code):
        mapping = SimpleNamespace(
            original_url=original_url,
            short_code=short_code,
        )
        self.created.append(mapping)
        return mapping


def test_generate_short_code_uses_default_length_and_allowed_characters():
    service = URLShortenerService()

    short_code = service.generate_short_code()

    assert len(short_code) == 6
    assert short_code.isalnum()


def test_create_short_url_returns_existing_mapping_for_duplicate_original_url():
    existing_mapping = SimpleNamespace(
        original_url="https://example.com/reused",
        short_code="reuse1",
    )
    service = URLShortenerService()
    fake_repository = FakeRepository(original_url_result=existing_mapping)
    service.repository = fake_repository

    mapping = service.create_short_url(
        db=object(),
        original_url="https://example.com/reused",
    )

    assert mapping is existing_mapping
    assert fake_repository.created == []


def test_create_short_url_retries_when_generated_short_code_already_exists(monkeypatch):
    service = URLShortenerService()
    fake_repository = FakeRepository(
        short_code_results=[
            SimpleNamespace(original_url="https://other.example", short_code="taken1"),
            None,
        ]
    )
    service.repository = fake_repository
    generated_codes = iter(["taken1", "open02"])
    monkeypatch.setattr(service, "generate_short_code", lambda: next(generated_codes))

    mapping = service.create_short_url(
        db=object(),
        original_url="https://example.com/new",
    )

    assert mapping.original_url == "https://example.com/new"
    assert mapping.short_code == "open02"
    assert len(fake_repository.created) == 1


def test_get_original_url_delegates_lookup_to_repository():
    expected_mapping = SimpleNamespace(
        original_url="https://example.com/found",
        short_code="found1",
    )
    service = URLShortenerService()
    service.repository = FakeRepository(short_code_results=[expected_mapping])

    mapping = service.get_original_url(db=object(), short_code="found1")

    assert mapping is expected_mapping
