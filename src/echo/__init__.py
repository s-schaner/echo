"""Echo AI proxy package."""

from .tmu import TMU, load_tmu, save_tmu
from .glyph import encode_glyph, decode_glyph
from .patterns import find_glyphs
from .interface import (
    create_memory_fragment,
    store_memory_fragment,
    load_memory_fragment,
    encode_text_as_glyph,
    decode_text_from_glyph,
    detect_glyphs_in_text,
)

__all__ = [
    "TMU",
    "load_tmu",
    "save_tmu",
    "encode_glyph",
    "decode_glyph",
    "find_glyphs",
    "create_memory_fragment",
    "store_memory_fragment",
    "load_memory_fragment",
    "encode_text_as_glyph",
    "decode_text_from_glyph",
    "detect_glyphs_in_text",
]
