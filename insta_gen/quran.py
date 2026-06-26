"""Client for the public `Al-Quran Cloud <https://alquran.cloud/api>`_ REST API.

A single request to the *editions* endpoint returns both the original Arabic
text and an English translation for a given ayah, which we model as a
:class:`Verse`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import requests

from insta_gen.config import TOTAL_AYAHS


@dataclass(frozen=True)
class Verse:
    """A single Qur'anic verse with its metadata.

    ``number`` is the global ayah index (1..6236); ``ayah_in_surah`` is the
    verse number within its chapter, so ``reference`` reads e.g. ``"Al-Faatiha
    1:1"``.
    """

    number: int
    arabic: str
    translation: str
    surah_number: int
    surah_name_arabic: str
    surah_name_english: str
    ayah_in_surah: int

    @property
    def reference(self) -> str:
        """Human-readable citation, e.g. ``"Al-Baqara 2:255"``."""
        return f"{self.surah_name_english} {self.surah_number}:{self.ayah_in_surah}"


class QuranAPIError(RuntimeError):
    """Raised when the Al-Quran Cloud API cannot be reached or returns bad data."""


class QuranClient:
    """Thin, typed wrapper around the Al-Quran Cloud API."""

    BASE_URL = "https://api.alquran.cloud/v1"
    ARABIC_EDITION = "quran-uthmani"
    TRANSLATION_EDITION = "en.asad"

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        self._timeout = timeout
        self._session = session or requests.Session()

    def get_verse(self, number: int) -> Verse:
        """Fetch a specific ayah by its global number (1..6236)."""
        if not 1 <= number <= TOTAL_AYAHS:
            raise ValueError(f"Ayah number must be in 1..{TOTAL_AYAHS}, got {number}")

        editions = f"{self.ARABIC_EDITION},{self.TRANSLATION_EDITION}"
        url = f"{self.BASE_URL}/ayah/{number}/editions/{editions}"

        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise QuranAPIError(f"Request to {url} failed: {exc}") from exc

        return self._parse(payload)

    def get_random_verse(self, rng: random.Random | None = None) -> Verse:
        """Fetch a uniformly random ayah from the whole Qur'an."""
        rng = rng or random.Random()
        return self.get_verse(rng.randint(1, TOTAL_AYAHS))

    @staticmethod
    def _parse(payload: dict) -> Verse:
        try:
            arabic_data, translation_data = payload["data"]
            surah = arabic_data["surah"]
            return Verse(
                number=arabic_data["number"],
                arabic=arabic_data["text"],
                translation=translation_data["text"],
                surah_number=surah["number"],
                surah_name_arabic=surah["name"],
                surah_name_english=surah["englishName"],
                ayah_in_surah=arabic_data["numberInSurah"],
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise QuranAPIError(f"Unexpected API response shape: {exc}") from exc
