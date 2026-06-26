"""Background-image generation via the OpenAI image API.

The OpenAI SDK is imported lazily so the rest of the package (verse fetching,
text rendering, tests) works without the dependency installed or an API key
configured.
"""

from __future__ import annotations

import base64
import io

import requests
from PIL import Image

# The default prompt keeps faces featureless (blank or silhouetted), consistent
# with the aniconism observed in Islamic visual tradition.
DEFAULT_PROMPT = (
    "A serene, contemplative scene with soft natural light and rich color — "
    "mountains, sky, water, architecture, or geometric Islamic patterns. "
    "Any human figures appear only as faceless silhouettes with no facial "
    "features. No text or lettering."
)


class ImageGenerationError(RuntimeError):
    """Raised when image generation or download fails."""


def build_openai_client(api_key: str | None = None) -> object:
    """Construct an OpenAI client, importing the SDK lazily.

    Shared by :class:`ImageGenerator` and the prompt composer. When ``api_key``
    is ``None`` the SDK falls back to the ``OPENAI_API_KEY`` environment
    variable, so both explicit and ambient configuration work.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - depends on env.
        raise ImageGenerationError(
            "The 'openai' package is required. Install it with 'pip install openai'."
        ) from exc
    return OpenAI(api_key=api_key) if api_key else OpenAI()


class ImageGenerator:
    """Generates a background image from a text prompt using OpenAI."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "gpt-image-1",
        size: str = "1024x1024",
        quality: str = "low",
        client: object | None = None,
        download_timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._size = size
        self._quality = quality
        self._download_timeout = download_timeout
        self._client = client or build_openai_client(api_key)

    def generate(self, prompt: str = DEFAULT_PROMPT) -> Image.Image:
        """Generate an image for ``prompt`` and return it as a PIL image."""
        try:
            response = self._client.images.generate(
                model=self._model,
                prompt=prompt,
                size=self._size,
                quality=self._quality,
                n=1,
            )
            datum = response.data[0]
        except Exception as exc:  # noqa: BLE001 - normalize SDK errors.
            raise ImageGenerationError(f"OpenAI image generation failed: {exc}") from exc

        # gpt-image-1 returns base64 bytes; dall-e models return a URL.
        b64 = getattr(datum, "b64_json", None)
        if b64:
            return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
        return self._download(datum.url)

    def _download(self, url: str) -> Image.Image:
        try:
            response = requests.get(url, timeout=self._download_timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ImageGenerationError(f"Failed to download image from {url}: {exc}") from exc
        return Image.open(io.BytesIO(response.content)).convert("RGB")
