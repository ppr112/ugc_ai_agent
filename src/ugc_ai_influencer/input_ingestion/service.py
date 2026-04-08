from __future__ import annotations

import re
from urllib.parse import urlparse

from ugc_ai_influencer.input_ingestion.fetcher import FetchedContent, UrlContentFetcher
from ugc_ai_influencer.models import InputKind, SourceBrief

URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)
DURATION_PATTERN = re.compile(r"(\d+)\s*-\s*second|(\d+)\s*second", re.IGNORECASE)
GENERIC_PRODUCT_PHRASES = {
    "ad",
    "ugc ad",
    "testimonial ad",
    "script",
    "script options",
    "video",
}


class InputIngestionService:
    def __init__(self, url_content_fetcher: UrlContentFetcher | None = None) -> None:
        self.url_content_fetcher = url_content_fetcher

    def parse(self, message_text: str) -> SourceBrief:
        cleaned = " ".join(message_text.strip().split())
        urls = URL_PATTERN.findall(cleaned)
        fetched_content = self._fetch_urls(urls)
        input_kind = self._classify_input(cleaned, urls)
        duration = self._extract_duration(cleaned)
        product = self._extract_product(cleaned, urls, fetched_content)
        audience = self._infer_audience(cleaned, fetched_content)
        pain_points = self._infer_pain_points(cleaned, fetched_content)
        benefits = self._infer_benefits(cleaned, fetched_content)
        tone = self._infer_tone(cleaned)
        summary = self._build_summary(cleaned, urls, product, audience, fetched_content)

        return SourceBrief(
            raw_input=cleaned,
            input_kind=input_kind,
            extracted_urls=urls,
            fetched_source_notes=[self._content_note(item) for item in fetched_content],
            product=product,
            audience=audience,
            pain_points=pain_points,
            benefits=benefits,
            tone=tone,
            desired_duration_seconds=duration,
            source_summary=summary,
        )

    def _classify_input(self, text: str, urls: list[str]) -> InputKind:
        if urls and len(text.replace(urls[0], "").strip()) > 0:
            return InputKind.MIXED
        if urls:
            return InputKind.URL
        return InputKind.TEXT

    def _fetch_urls(self, urls: list[str]) -> list[FetchedContent]:
        if not urls or self.url_content_fetcher is None:
            return []

        fetched: list[FetchedContent] = []
        for url in urls[:2]:
            try:
                fetched.append(self.url_content_fetcher.fetch(url))
            except RuntimeError:
                continue
        return fetched

    def _extract_duration(self, text: str) -> int:
        match = DURATION_PATTERN.search(text)
        if not match:
            return 20
        return int(next(group for group in match.groups() if group))

    def _extract_product(
        self,
        text: str,
        urls: list[str],
        fetched_content: list[FetchedContent],
    ) -> str:
        lowered = text.lower()
        starters = (
            "make me a",
            "make a",
            "create a",
            "turn this website into a",
            "turn this into a",
            "give me",
        )
        stripped = lowered
        for starter in starters:
            if stripped.startswith(starter):
                stripped = stripped[len(starter) :].strip()
                break

        stripped = URL_PATTERN.sub("", stripped).strip(" .")
        normalized = re.sub(r"\s+", " ", stripped).strip()
        if normalized in GENERIC_PRODUCT_PHRASES and fetched_content:
            title = fetched_content[0].title.split("|")[0].split("-")[0].strip()
            return title or "product from provided source"
        if not normalized and urls:
            if fetched_content:
                title = fetched_content[0].title.split("|")[0].split("-")[0].strip()
                return title or "product from provided source"
            hostname = urlparse(urls[0]).netloc.replace("www.", "")
            return hostname or "product from provided source"

        tokens = normalized.split()
        if not tokens:
            return "your product"
        return " ".join(tokens[:6]).strip()

    def _infer_audience(self, text: str, fetched_content: list[FetchedContent]) -> str:
        lowered = self._combined_text(text, fetched_content).lower()
        if "skincare" in lowered:
            return "people looking for a simple skincare routine"
        if "protein" in lowered or "fitness" in lowered:
            return "health-conscious shoppers who want convenient results"
        if "saas" in lowered or "software" in lowered:
            return "busy operators evaluating tools that save time"
        if "shop" in lowered or "ecommerce" in lowered:
            return "online shoppers comparing products before buying"
        return "social-first shoppers who respond to authentic product demos"

    def _infer_pain_points(self, text: str, fetched_content: list[FetchedContent]) -> list[str]:
        lowered = self._combined_text(text, fetched_content).lower()
        suggestions = []
        if "skincare" in lowered:
            suggestions.extend(
                [
                    "Too many products with confusing routines",
                    "Concern about irritation or breakouts",
                ]
            )
        if "testimonial" in lowered:
            suggestions.append("Skepticism about whether the product really works")
        if "slow" in lowered or "time" in lowered:
            suggestions.append("Users are frustrated by workflows that take too long")
        if not suggestions:
            suggestions.extend(
                [
                    "People ignore generic ads",
                    "Shoppers want proof before they trust a claim",
                ]
            )
        return suggestions

    def _infer_benefits(self, text: str, fetched_content: list[FetchedContent]) -> list[str]:
        lowered = self._combined_text(text, fetched_content).lower()
        suggestions = []
        if "skincare" in lowered:
            suggestions.extend(
                [
                    "Simple routine that feels easy to stick with",
                    "Visible glow or smoother skin with consistent use",
                ]
            )
        if "testimonial" in lowered:
            suggestions.append("Real-user framing that feels trustworthy")
        if "save time" in lowered or "faster" in lowered:
            suggestions.append("Clear time-saving payoff users can feel quickly")
        if not suggestions:
            suggestions.extend(
                [
                    "Fast understanding of the product value",
                    "Native-feeling ad creative for short-form video",
                ]
            )
        return suggestions

    def _infer_tone(self, text: str) -> str:
        lowered = text.lower()
        if "testimonial" in lowered:
            return "credible, warm, and experience-led"
        if "ad" in lowered:
            return "punchy, casual, and creator-native"
        return "friendly, clear, and conversational"

    def _build_summary(
        self,
        text: str,
        urls: list[str],
        product: str,
        audience: str,
        fetched_content: list[FetchedContent],
    ) -> str:
        source_notes = " ".join(self._content_note(item) for item in fetched_content)
        if urls:
            return (
                f"Use the user message plus source URLs to create a concise UGC ad brief for "
                f"{product} aimed at {audience}. Source links: {', '.join(urls)}. "
                f"Source context: {source_notes or 'No extra page context captured.'}"
            )
        return (
            f"Use the user message to create a concise UGC ad brief for {product} aimed at "
            f"{audience}. Original request: {text}"
        )

    def _combined_text(self, text: str, fetched_content: list[FetchedContent]) -> str:
        fetched_text = " ".join(f"{item.title} {item.excerpt}" for item in fetched_content)
        return f"{text} {fetched_text}".strip()

    def _content_note(self, item: FetchedContent) -> str:
        return f"{item.title}: {item.excerpt[:220]}"
