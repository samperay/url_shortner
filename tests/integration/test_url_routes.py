def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_renders_form(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Shorten URL" in response.text
    assert 'name="original_url"' in response.text


def test_shorten_url_creates_mapping_and_displays_short_url(client):
    response = client.post(
        "/shorten",
        data={"original_url": "https://example.com/some/long/path"},
    )

    assert response.status_code == 200
    assert "https://example.com/some/long/path" in response.text
    assert "http://testserver/" in response.text


def test_duplicate_original_url_reuses_existing_short_code(client):
    first_response = client.post(
        "/shorten",
        data={"original_url": "https://example.com/duplicate"},
    )
    second_response = client.post(
        "/shorten",
        data={"original_url": "https://example.com/duplicate"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    first_short_url = _extract_short_url(first_response.text)
    second_short_url = _extract_short_url(second_response.text)
    assert first_short_url == second_short_url


def test_redirect_to_original_url_returns_redirect_response(client):
    response = client.post(
        "/shorten",
        data={"original_url": "https://example.com/redirect-target"},
    )
    short_url = _extract_short_url(response.text)
    short_code = short_url.rstrip("/").split("/")[-1]

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/redirect-target"


def test_redirect_to_missing_short_code_returns_404(client):
    response = client.get("/missing-code")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


def _extract_short_url(response_text):
    marker = "http://testserver/"
    start = response_text.index(marker)
    end = response_text.index("<", start)
    return response_text[start:end].strip()
