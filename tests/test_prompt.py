"""Tests for verse-to-prompt composition using an injected fake OpenAI client."""

from __future__ import annotations

from types import SimpleNamespace

from insta_gen.images import DEFAULT_PROMPT
from insta_gen.prompt import SAFETY_SUFFIX, VersePromptComposer
from insta_gen.quran import Verse

VERSE = Verse(
    number=1,
    arabic="بِسْمِ اللَّهِ",
    translation="In the name of God, the Most Gracious, the Most Merciful",
    surah_number=1,
    surah_name_arabic="الفاتحة",
    surah_name_english="Al-Faatiha",
    ayah_in_surah=1,
)


class _FakeChatClient:
    """Minimal stand-in for the OpenAI client's chat.completions.create."""

    def __init__(self, content: str | None = "A calm dawn over still water.", error: bool = False):
        self._content = content
        self._error = error
        self.last_kwargs: dict | None = None

        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        response = SimpleNamespace(choices=[choice])

        def create(**kwargs):
            self.last_kwargs = kwargs
            if self._error:
                raise RuntimeError("boom")
            return response

        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))


def test_compose_appends_safety_suffix_and_uses_verse():
    client = _FakeChatClient(content="A calm dawn over still water.")
    composer = VersePromptComposer(client=client, model="gpt-4o-mini")

    prompt = composer.compose(VERSE)

    assert prompt == f"A calm dawn over still water. {SAFETY_SUFFIX}"
    # The verse translation must reach the model.
    user_msg = client.last_kwargs["messages"][-1]["content"]
    assert VERSE.translation in user_msg
    assert VERSE.reference in user_msg
    assert client.last_kwargs["model"] == "gpt-4o-mini"


def test_compose_falls_back_to_default_on_error():
    composer = VersePromptComposer(client=_FakeChatClient(error=True))
    assert composer.compose(VERSE) == DEFAULT_PROMPT


def test_compose_falls_back_when_model_returns_empty():
    composer = VersePromptComposer(client=_FakeChatClient(content="   "))
    assert composer.compose(VERSE) == DEFAULT_PROMPT
