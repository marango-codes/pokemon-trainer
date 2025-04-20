"""
Unit tests for core.rom_utils (ROM checksum validation).
"""
import tempfile
import os
from core import rom_utils

def test_compute_sha256_expected():
    # Create a temp file with known content
    data = b"test1234"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        f.flush()
        sha = rom_utils.compute_sha256(f.name)
    assert sha == rom_utils.compute_sha256(f.name)
    os.remove(f.name)

def test_is_valid_pokemon_red_rom_edge():
    # Should return False for a file with wrong contents
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"not a rom")
        f.flush()
        assert not rom_utils.is_valid_pokemon_red_rom(f.name)
    os.remove(f.name)
