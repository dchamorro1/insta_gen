"""Tests for the pure rendering logic (no network or API key required)."""

from __future__ import annotations

from PIL import Image, ImageFont

from insta_gen.config import DEFAULT_FONT_PATH
from insta_gen.overlay import render_verse, wrap_text
from insta_gen.quran import Verse

FONT = ImageFont.truetype(str(DEFAULT_FONT_PATH), 40)


def _verse(translation: str = "In the name of God, the Most Gracious, the Most Merciful") -> Verse:
    return Verse(
        number=1,
        arabic="بِسْمِ اللَّهِ",
        translation=translation,
        surah_number=1,
        surah_name_arabic="الفاتحة",
        surah_name_english="Al-Faatiha",
        ayah_in_surah=1,
    )


def test_wrap_text_keeps_every_line_within_max_width():
    text = "the quick brown fox jumps over the lazy dog again and again"
    max_width = 200.0

    lines = wrap_text(text, FONT, max_width)

    assert lines, "expected at least one line"
    assert " ".join(lines).split() == text.split(), "no words lost or reordered"
    for line in lines:
        assert FONT.getlength(line) <= max_width


def test_wrap_text_places_overlong_word_on_its_own_line():
    long_word = "supercalifragilisticexpialidocious"
    lines = wrap_text(long_word, FONT, max_width=50.0)
    assert lines == [long_word]


def test_wrap_text_empty_string_returns_no_lines():
    assert wrap_text("   ", FONT, max_width=100.0) == []


def test_render_verse_returns_same_size_image():
    background = Image.new("RGB", (1024, 1024), color="navy")

    result = render_verse(
        background,
        _verse(),
        font_path=DEFAULT_FONT_PATH,
        font_size=50,
    )

    assert result.size == (1024, 1024)
    assert result.mode == "RGB"
    # Rendering must not mutate the caller's image.
    assert background.getpixel((512, 512)) == (0, 0, 128)


def test_verse_reference_formatting():
    assert _verse().reference == "Al-Faatiha 1:1"
