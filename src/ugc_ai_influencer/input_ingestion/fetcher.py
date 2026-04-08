from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(slots=True)
class FetchedContent:
    url: str
    title: str
    excerpt: str


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""
        self.text_parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self.in_title:
            self.title = f"{self.title} {cleaned}".strip()
            return
        self.text_parts.append(cleaned)


class UrlContentFetcher:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> FetchedContent:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; UGCInfluencerBot/0.1; +https://example.invalid/bot)"
                )
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8", errors="ignore")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc

        parser = _HTMLTextExtractor()
        parser.feed(raw)
        body_text = " ".join(parser.text_parts)
        excerpt = self._clean_text(body_text)[:900]
        title = self._clean_text(parser.title) or "Untitled page"
        return FetchedContent(url=url, title=title, excerpt=excerpt or "No readable body text found.")

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
