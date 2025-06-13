# Echo

Echo is an offline proxy designed to manage symbolic memory units and glyphs for the Aurora project.

The `echo` Python package provides utilities for:

- Handling **Token Memory Units** (TMUs) stored as JSON files.
- Encoding and decoding glyphs used to preserve identity and meaning.
- Detecting glyph-like patterns within text.
- Creating and storing memory fragments to disk.

## Installation

This repository uses a simple `src` layout. You can install the package in editable mode using:

```bash
pip install -e .
```

## Example

```python
from echo import (
    create_memory_fragment,
    store_memory_fragment,
    encode_text_as_glyph,
    decode_text_from_glyph,
    detect_glyphs_in_text,
)

# create a memory fragment and store it
tmu = create_memory_fragment("Hello world")
store_memory_fragment(tmu, "memory")

# encode and decode a glyph
glyph = encode_text_as_glyph("sample")
text = decode_text_from_glyph(glyph)
print(glyph, text)

# detect glyph-like tokens
print(detect_glyphs_in_text("Alpha-0x7F meets Zeta-V0ID"))
```
