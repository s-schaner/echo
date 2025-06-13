from echo import (
    create_memory_fragment,
    encode_text_as_glyph,
    decode_text_from_glyph,
    detect_glyphs_in_text,
)


def test_memory_fragment_roundtrip(tmp_path):
    tmu = create_memory_fragment("hi")
    path = tmp_path / "tmu.json"
    from echo import store_memory_fragment, load_memory_fragment
    store_memory_fragment(tmu, tmp_path)
    loaded = load_memory_fragment(tmu.id, tmp_path)
    assert loaded.content == "hi"


def test_glyph_encoding():
    glyph = encode_text_as_glyph("data")
    assert decode_text_from_glyph(glyph) == "data"


def test_detect_glyphs():
    text = "Alpha-0x7F meets Beta-1"
    assert detect_glyphs_in_text(text) == ["Alpha-0x7F", "Beta-1"]
