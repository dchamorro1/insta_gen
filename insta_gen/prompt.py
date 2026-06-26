"""Verse-to-image-prompt composition.

Turns a :class:`~insta_gen.quran.Verse` into a vivid scene description suitable
for an image generator, using an OpenAI chat model. This is the first stage of
the two-step pipeline (interpret → generate), letting the background actually
reflect what the verse is about.
"""

from __future__ import annotations

import logging

from insta_gen.images import DEFAULT_PROMPT, build_openai_client
from insta_gen.quran import Verse

logger = logging.getLogger(__name__)

# Reinforced on the final prompt regardless of what the model returns.
SAFETY_SUFFIX = (
    "Any people or figures must have no discernible facial features — render faces "
    "as blank, obscured, turned away, or as silhouettes. No text, words, or lettering."
)

_SYSTEM_PROMPT = (
    "You write prompts for an image generator. Given an English translation of a "
    "verse of the Qur'an, produce ONE concise prompt (2-4 sentences) describing a "
    "single evocative background scene that captures the verse's mood and themes. "
    "Choose whatever visual style best fits the verse (atmospheric natural "
    "landscape, Islamic geometric or architectural art, abstract symbolic "
    "composition, etc.). Absolute rules: people and figures may appear, but they "
    "must have NO discernible facial features — render faces as blank, obscured, "
    "turned away, or as silhouettes; include NO text, words, letters, or "
    "calligraphy in the image; keep the scene respectful and contemplative. "
    "Output only the image prompt, with no preamble or quotation marks."
)


class VersePromptComposer:
    """Composes an image prompt from a verse via an OpenAI chat model."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        client: object | None = None,
    ) -> None:
        self._model = model
        self._client = client or build_openai_client(api_key)

    def compose(self, verse: Verse) -> str:
        """Return an image-generation prompt describing a scene for ``verse``.

        Falls back to the generic :data:`DEFAULT_PROMPT` if the model call fails,
        so background generation degrades gracefully rather than aborting.
        """
        user_message = f'Verse {verse.reference}: "{verse.translation}"'
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.8,
            )
            scene = (response.choices[0].message.content or "").strip()
        except Exception as exc:  # noqa: BLE001 - normalize SDK errors.
            logger.warning("Prompt composition failed (%s); using default prompt.", exc)
            return DEFAULT_PROMPT

        if not scene:
            logger.warning("Prompt composition returned empty text; using default prompt.")
            return DEFAULT_PROMPT

        return f"{scene} {SAFETY_SUFFIX}"
