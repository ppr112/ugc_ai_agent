from __future__ import annotations

import unittest

from ugc_ai_influencer.telegram_interface.handlers import build_image_prompt


class HandlerTests(unittest.TestCase):
    def test_build_image_prompt_uses_caption_when_present(self) -> None:
        prompt = build_image_prompt("Make this into an ad", "Visible serum bottle with bright packaging")
        self.assertIn("Make this into an ad", prompt)
        self.assertIn("Image analysis:", prompt)

    def test_build_image_prompt_falls_back_when_caption_missing(self) -> None:
        prompt = build_image_prompt("", "Visible product close-up")
        self.assertIn("Create a UGC ad from this product image.", prompt)
