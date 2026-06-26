"""Orchestration: fetch a verse, obtain a background, compose, and save.

The default flow is a two-step AI pipeline:

    verse  →  (chat model writes a scene description)  →  (image model renders it)

so the background reflects what the verse is about. Keeping the glue here
(rather than in the CLI) makes the full flow importable and testable.
"""

from __future__ import annotations

import logging
import random
import secrets
from pathlib import Path

from PIL import Image

from insta_gen.config import Settings
from insta_gen.images import ImageGenerator
from insta_gen.overlay import render_verse
from insta_gen.prompt import VersePromptComposer
from insta_gen.quran import QuranClient, Verse

logger = logging.getLogger(__name__)


def _unique_output_path(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = secrets.token_hex(3)
    return output_dir / f"verse_{suffix}.png"


def _generate_background(settings: Settings, verse: Verse, prompt: str | None) -> Image.Image:
    """Generate a background for ``verse``.

    When ``prompt`` is ``None`` a verse-specific prompt is composed by the chat
    model; otherwise the caller-supplied prompt is used verbatim.
    """
    if prompt is None:
        composer = VersePromptComposer(
            api_key=settings.openai_api_key,
            model=settings.text_model,
        )
        prompt = composer.compose(verse)
        logger.info("Composed prompt: %s", prompt)

    logger.info("Generating background with %s", settings.openai_model)
    generator = ImageGenerator(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        size=settings.image_size,
        quality=settings.image_quality,
    )
    return generator.generate(prompt)


def create_post(
    *,
    settings: Settings | None = None,
    background_path: Path | None = None,
    prompt: str | None = None,
    seed: int | None = None,
    quran_client: QuranClient | None = None,
) -> tuple[Path, Verse]:
    """Create a single verse image and return its path and the chosen verse.

    Parameters
    ----------
    settings:
        Runtime configuration. Defaults to :meth:`Settings.from_env`.
    background_path:
        If given, this image is used as the background instead of generating
        one (no OpenAI key required).
    prompt:
        If ``None`` (default), a verse-specific prompt is composed by the chat
        model. Pass a string to override that and generate from a fixed prompt.
    seed:
        Optional seed for reproducible verse selection.
    quran_client:
        Injectable client, primarily for testing.
    """
    settings = settings or Settings.from_env()
    quran_client = quran_client or QuranClient()
    rng = random.Random(seed) if seed is not None else None

    verse = quran_client.get_random_verse(rng)
    logger.info("Selected %s (ayah #%d)", verse.reference, verse.number)

    if background_path is not None:
        logger.info("Using background image: %s", background_path)
        background = Image.open(background_path).convert("RGB")
    else:
        background = _generate_background(settings, verse, prompt)

    image = render_verse(
        background,
        verse,
        font_path=settings.font_path,
        font_size=settings.font_size,
    )

    output_path = _unique_output_path(settings.output_dir)
    image.save(output_path)
    logger.info("Saved %s", output_path)
    return output_path, verse
