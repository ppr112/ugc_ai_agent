from __future__ import annotations

import unittest

from ugc_ai_influencer.input_ingestion.fetcher import FetchedContent
from ugc_ai_influencer.input_ingestion.service import InputIngestionService
from ugc_ai_influencer.models import InputKind


class FakeFetcher:
    def fetch(self, url: str) -> FetchedContent:
        return FetchedContent(
            url=url,
            title="Glow Serum",
            excerpt="A lightweight skincare serum for smoother skin and a faster routine.",
        )


class InputIngestionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = InputIngestionService()

    def test_parse_text_request(self) -> None:
        brief = self.service.parse("Make me a 20-second skincare UGC ad")
        self.assertEqual(brief.input_kind, InputKind.TEXT)
        self.assertEqual(brief.desired_duration_seconds, 20)
        self.assertIn("skincare", brief.product)
        self.assertTrue(brief.pain_points)

    def test_parse_url_request(self) -> None:
        brief = self.service.parse("Turn this website into a testimonial ad https://example.com")
        self.assertEqual(brief.input_kind, InputKind.MIXED)
        self.assertEqual(brief.extracted_urls, ["https://example.com"])
        self.assertIn("example.com", brief.source_summary)

    def test_parse_url_request_with_fetched_context(self) -> None:
        service = InputIngestionService(url_content_fetcher=FakeFetcher())
        brief = service.parse("Turn this website into a testimonial ad https://example.com")
        self.assertEqual(brief.product, "Glow Serum")
        self.assertTrue(brief.fetched_source_notes)
        self.assertIn("Glow Serum", brief.source_summary)
