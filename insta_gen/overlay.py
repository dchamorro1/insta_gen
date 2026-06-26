"""Text composition: render a verse onto a background image with Pillow.

The wrapping logic is factored into a pure :func:`wrap_text` helper so it can be
unit-tested without performing any I/O.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from insta_gen.quran import Verse

# Colours and outline used when drawing the verse text.
TEXT_COLOR = "white"
OUTLINE_COLOR = "black"
OUTLINE_WIDTH = 2
LINE_SPACING = 8
SIDE_MARGIN = 50


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> list[str]:
    """Greedily wrap ``text`` so each rendered line fits within ``max_width`` px.

    A single word longer than ``max_width`` is placed on its own line rather
    than being dropped.
    """
    lines: list[str] = []
    current: list[str] = []

    for word in text.split():
        candidate = " ".join((*current, word))
        if current and font.getlength(candidate) > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        lines.append(" ".join(current))
    return lines


def _line_height(font: ImageFont.FreeTypeFont) -> int:
    ascent, descent = font.getmetrics()
    return ascent + descent + LINE_SPACING


def render_verse(
    background: Image.Image,
    verse: Verse,
    *,
    font_path: Path,
    font_size: int,
) -> Image.Image:
    """Return a copy of ``background`` with ``verse`` rendered onto it.

    The English translation is centred as a wrapped, outlined block and the
    citation (e.g. ``"Al-Faatiha 1:1"``) is drawn beneath it.
    """
    image = background.convert("RGB").copy()
    draw = ImageDraw.Draw(image)
    width, height = image.size

    font = ImageFont.truetype(str(font_path), font_size)
    ref_font = ImageFont.truetype(str(font_path), max(font_size // 2, 16))

    max_width = width - 2 * SIDE_MARGIN
    lines = wrap_text(verse.translation, font, max_width)

    line_height = _line_height(font)
    block_height = line_height * len(lines)
    # Vertically centre the verse block, leaving room for the citation below.
    y = (height - block_height) // 2

    for line in lines:
        line_width = font.getlength(line)
        x = (width - line_width) / 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=TEXT_COLOR,
            stroke_width=OUTLINE_WIDTH,
            stroke_fill=OUTLINE_COLOR,
        )
        y += line_height

    _draw_reference(draw, verse.reference, ref_font, width, y + LINE_SPACING)
    return image


def _draw_reference(
    draw: ImageDraw.ImageDraw,
    reference: str,
    font: ImageFont.FreeTypeFont,
    width: int,
    y: float,
) -> None:
    ref_width = font.getlength(reference)
    draw.text(
        ((width - ref_width) / 2, y),
        reference,
        font=font,
        fill=TEXT_COLOR,
        stroke_width=1,
        stroke_fill=OUTLINE_COLOR,
    )
