"""insta_gen: generate shareable images that pair an AI-generated background
with a randomly selected verse of the Qur'an.

The package is split into small, single-responsibility modules:

* :mod:`insta_gen.config`    – environment-driven settings
* :mod:`insta_gen.quran`     – client for the Al-Quran Cloud REST API
* :mod:`insta_gen.images`    – background generation via the OpenAI image API
* :mod:`insta_gen.overlay`   – Pillow text-composition / rendering
* :mod:`insta_gen.pipeline`  – orchestration that ties the pieces together
"""

from insta_gen.config import Settings
from insta_gen.quran import QuranClient, Verse

__all__ = ["Settings", "QuranClient", "Verse"]
__version__ = "1.0.0"
