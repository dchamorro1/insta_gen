"""Command-line entry point: ``python -m insta_gen`` (or ``insta-gen``)."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from insta_gen.config import Settings
from insta_gen.pipeline import create_post


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="insta-gen",
        description="Generate an image pairing a random Qur'an verse with a background.",
    )
    parser.add_argument(
        "-b",
        "--background",
        type=Path,
        default=None,
        help="Path to an existing background image. If omitted, one is generated "
        "with OpenAI (requires OPENAI_API_KEY).",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        default=None,
        help="Override the auto-composed prompt with a fixed one. By default a "
        "chat model writes a prompt describing a scene for the chosen verse.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write the result into (defaults to ./generated_images).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for reproducible verse selection.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable info-level logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    settings = Settings.from_env()
    if args.output_dir is not None:
        settings = replace_output_dir(settings, args.output_dir)

    try:
        output_path, verse = create_post(
            settings=settings,
            background_path=args.background,
            prompt=args.prompt,
            seed=args.seed,
        )
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error.
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"{verse.reference}\n{verse.arabic}\n{verse.translation}\n→ {output_path}")
    return 0


def replace_output_dir(settings: Settings, output_dir: Path) -> Settings:
    """Return a copy of ``settings`` with ``output_dir`` overridden."""
    from dataclasses import replace

    return replace(settings, output_dir=output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
