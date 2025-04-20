"""
Unit tests for core.emulator (PokemonRedGameWrapper).
"""
import pytest
from core.emulator import PokemonRedGameWrapper, ROM_PATH

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_emulator_loads_expected():
    env = PokemonRedGameWrapper()
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_emulator_debug_logging():
    env = PokemonRedGameWrapper(debug=True)
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_emulator_invalid_rom_failure(tmp_path):
    # Copy ROM to temp and corrupt it
    rom = tmp_path / "bad.gb"
    rom.write_bytes(b"not a rom")
    with pytest.raises(ValueError):
        PokemonRedGameWrapper(rom_path=rom)
