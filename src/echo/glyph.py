import base64

GLYPH_PREFIX = "glyph:"


def encode_glyph(text: str) -> str:
    """Encode text into a glyph string."""
    encoded = base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")
    return f"{GLYPH_PREFIX}{encoded}"


def decode_glyph(glyph: str) -> str:
    """Decode a glyph string back into text."""
    if not glyph.startswith(GLYPH_PREFIX):
        raise ValueError("Invalid glyph")
    data = glyph[len(GLYPH_PREFIX):]
    return base64.urlsafe_b64decode(data.encode("ascii")).decode("utf-8")
