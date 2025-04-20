"""
Unit tests for core.pyboy_env (PyBoyEnv wrapper).
"""
import pytest
from core.emulator import PyBoyEnv, ROM_PATH

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_pyboy_env_loads_expected():
    env = PyBoyEnv()
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_pyboy_env_invalid_rom_failure(tmp_path):
    # Copy ROM to temp and corrupt it
    rom = tmp_path / "bad.gb"
    rom.write_bytes(b"not a rom")
    with pytest.raises(ValueError):
        PyBoyEnv(rom_path=rom)
