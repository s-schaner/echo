import re
from typing import Iterable

GLYPH_PATTERN = re.compile(r"[A-Za-z]+-[A-Za-z0-9]+")


def find_glyphs(text: str) -> Iterable[str]:
    """Yield glyph-like patterns from text."""
    return GLYPH_PATTERN.findall(text)
