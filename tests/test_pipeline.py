"""Integration test for create_post wiring, with all I/O faked (no network)."""

from __future__ import annotations

from PIL import Image

from insta_gen import pipeline
from insta_gen.config import Settings
from insta_gen.quran import Verse

VERSE = Verse(
    number=42,
    arabic="بِسْمِ اللَّهِ",
    translation="In the name of God, the Most Gracious, the Most Merciful",
    surah_number=1,
    surah_name_arabic="الفاتحة",
    surah_name_english="Al-Faatiha",
    ayah_in_surah=1,
)


class _FakeQuran:
    def get_random_verse(self, rng=None):
        return VERSE


class _FakeComposer:
    last_verse = None

    def __init__(self, **kwargs):
        pass

    def compose(self, verse):
        _FakeComposer.last_verse = verse
        return "a serene composed scene"


class _RecordingGenerator:
    received_prompt = None

    def __init__(self, **kwargs):
        pass

    def generate(self, prompt):
        _RecordingGenerator.received_prompt = prompt
        return Image.new("RGB", (1024, 1024), color="teal")


def test_create_post_composes_prompt_and_saves(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "VersePromptComposer", _FakeComposer)
    monkeypatch.setattr(pipeline, "ImageGenerator", _RecordingGenerator)

    settings = Settings(openai_api_key="test", output_dir=tmp_path)

    output_path, verse = pipeline.create_post(
        settings=settings,
        quran_client=_FakeQuran(),
    )

    assert verse == VERSE
    assert output_path.exists()
    assert output_path.parent == tmp_path
    # The verse-specific composed prompt must flow into image generation.
    assert _FakeComposer.last_verse == VERSE
    assert _RecordingGenerator.received_prompt == "a serene composed scene"


def test_create_post_with_explicit_prompt_skips_composer(monkeypatch, tmp_path):
    _RecordingGenerator.received_prompt = None
    monkeypatch.setattr(pipeline, "ImageGenerator", _RecordingGenerator)

    # If the composer were called it would raise, proving it was skipped.
    def _boom(**kwargs):
        raise AssertionError("composer should not be constructed")

    monkeypatch.setattr(pipeline, "VersePromptComposer", _boom)

    settings = Settings(openai_api_key="test", output_dir=tmp_path)
    pipeline.create_post(
        settings=settings,
        prompt="a fixed prompt",
        quran_client=_FakeQuran(),
    )

    assert _RecordingGenerator.received_prompt == "a fixed prompt"
