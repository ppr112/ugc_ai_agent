# UGC AI Influencer Telegram Agent

Production-minded Python MVP for a Telegram bot that turns user input into UGC-style ad concepts, scripts, and video-generation packages.

## What This MVP Does

- Accepts free-form text, URLs, and product images from Telegram users.
- Extracts source context into a normalized brief, including basic webpage text scraping.
- Can analyze product photos and turn them into a usable prompt for UGC script generation.
- Generates:
  - product summary
  - audience and pain points
  - creative angles
  - UGC scripts
  - CTA
  - shot plan
  - avatar/video generation instructions
- Persists jobs to disk.
- Returns a Telegram-friendly summary plus an output package path.

## Architecture

```text
Telegram -> Ingestion/Image Analysis -> Creative Strategy -> Script Engine -> Media Generation -> Storage -> Telegram Reply
```

Modules:

- `telegram_interface`: bot entrypoint and handlers
- `input_ingestion`: input classification, URL extraction, and webpage normalization
- `image_analysis`: product-photo analysis for image messages
- `creative_strategy`: marketing angles and positioning
- `script_engine`: script, CTA, and shot plan generation
- `media_generation`: creates a render package for downstream video tools
- `orchestration`: coordinates end-to-end jobs
- `storage`: JSON-backed job persistence
- `config`: environment-driven settings
- `llm`: provider-based structured generation layer

## Quick Start

1. Create a virtual environment.
2. Install dependencies.
3. Copy `.env.example` to `.env`.
4. Add your Telegram bot token from BotFather.
5. Run the bot.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
python3 -m ugc_ai_influencer.main
```

## Current MVP Behavior

- `LLM_PROVIDER=mock` keeps generation deterministic and local.
- `LLM_PROVIDER=openai` uses the OpenAI Responses API with structured JSON output.
- `OPENAI_VISION_MODEL` is used for image analysis.
- `MEDIA_PROVIDER=mock` produces a JSON render package instead of a real video.
- URL messages can be enriched with fetched page title and readable body text.
- Photo messages can be analyzed and converted into the same UGC pipeline.

## LLM Modes

- `LLM_PROVIDER=mock`: no external API call, safe for local development
- `LLM_PROVIDER=openai`: uses `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_VISION_MODEL`

Example:

```bash
LLM_PROVIDER=openai OPENAI_MODEL=gpt-4o-mini OPENAI_VISION_MODEL=gpt-4.1-mini python3 -m ugc_ai_influencer.main
```

## Example Requests

- `Make me a 20-second skincare UGC ad`
- `Turn this website into a testimonial ad https://example.com`
- Send a product image with caption: `Make this into a UGC testimonial ad`

## Project Structure

```text
src/ugc_ai_influencer/
  config.py
  logging_config.py
  main.py
  models.py
  creative_strategy/
  image_analysis/
  input_ingestion/
  llm/
  media_generation/
  orchestration/
  storage/
  telegram_interface/
tests/
```

## Running Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Next Production Steps

1. Add YouTube transcript ingestion.
2. Connect a real avatar/video rendering API in `media_generation`.
3. Move from JSON files to Postgres or Redis-backed job storage.
4. Add async worker queues for long-running renders.
5. Add approval-safe observability for external provider failures.
