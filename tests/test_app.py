import asyncio
from html.parser import HTMLParser

import httpx

from app.main import app


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.form_count = 0
        self.body_depth = 0
        self.controls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "body":
            self.body_depth += 1
        elif tag == "form" and self.body_depth:
            self.form_count += 1
        elif tag in {"input", "button", "textarea", "select"} and self.body_depth:
            self.controls.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "body":
            self.body_depth -= 1


def request(path: str) -> httpx.Response:
    async def make_request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(make_request())


def test_health_endpoint_returns_success() -> None:
    response = request("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_html_with_form() -> None:
    response = request("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")

    parser = FormParser()
    parser.feed(response.text)
    assert parser.form_count == 1
    assert parser.controls
