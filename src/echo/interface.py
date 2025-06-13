from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict

from .tmu import TMU, save_tmu, load_tmu
from .glyph import encode_glyph, decode_glyph
from .patterns import find_glyphs


def create_memory_fragment(text: str, metadata: Dict[str, Any] | None = None) -> TMU:
    """Create a TMU from raw text."""
    fragment_id = str(uuid.uuid4())
    return TMU(id=fragment_id, content=text, metadata=metadata)


def store_memory_fragment(tmu: TMU, directory: str | Path) -> Path:
    """Store TMU as a JSON file within a directory."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{tmu.id}.json"
    save_tmu(tmu, path)
    return path


def load_memory_fragment(fragment_id: str, directory: str | Path) -> TMU:
    """Load TMU from a directory by id."""
    path = Path(directory) / f"{fragment_id}.json"
    return load_tmu(path)


def encode_text_as_glyph(text: str) -> str:
    """Encode text as a glyph."""
    return encode_glyph(text)


def decode_text_from_glyph(glyph: str) -> str:
    """Decode text from a glyph."""
    return decode_glyph(glyph)


def detect_glyphs_in_text(text: str) -> list[str]:
    """Return all glyph-like patterns in text."""
    return list(find_glyphs(text))
