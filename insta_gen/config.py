"""Application configuration.

All tunable values live here and are sourced from environment variables so the
same code runs unchanged across local development and CI/production. A local
``.env`` file is loaded automatically when ``python-dotenv`` is installed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # Optional convenience: load a local .env if python-dotenv is available.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is an optional dependency.
    pass

# Project layout anchors.
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

# The Qur'an contains exactly 6,236 verses (ayahs) across its 114 chapters.
TOTAL_AYAHS = 6236

# The English translation is rendered in a clean, legible sans-serif. The
# bundled Aalmaghribi calligraphy font is reserved for Arabic rendering, for
# which its decorative swashes are appropriate.
DEFAULT_FONT_PATH = ASSETS_DIR / "DejaVuSans.ttf"
ARABIC_FONT_PATH = ASSETS_DIR / "AalmaghribiQuran.ttf"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "generated_images"


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser() if value else default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    """Immutable, environment-driven configuration for a pipeline run."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-image-1"
    # Cheapest gpt-image-1 tier; also accepts "medium"/"high".
    image_quality: str = "low"
    # Chat model that interprets a verse into an image-generation prompt.
    text_model: str = "gpt-4o-mini"
    image_size: str = "1024x1024"
    font_path: Path = DEFAULT_FONT_PATH
    font_size: int = 50
    output_dir: Path = DEFAULT_OUTPUT_DIR

    @classmethod
    def from_env(cls) -> "Settings":
        """Build a :class:`Settings` instance from the process environment."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("INSTA_GEN_OPENAI_MODEL", "gpt-image-1"),
            image_quality=os.getenv("INSTA_GEN_IMAGE_QUALITY", "low"),
            text_model=os.getenv("INSTA_GEN_TEXT_MODEL", "gpt-4o-mini"),
            image_size=os.getenv("INSTA_GEN_IMAGE_SIZE", "1024x1024"),
            font_path=_env_path("INSTA_GEN_FONT_PATH", DEFAULT_FONT_PATH),
            font_size=_env_int("INSTA_GEN_FONT_SIZE", 50),
            output_dir=_env_path("INSTA_GEN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
        )
