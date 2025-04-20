"""
ROM utilities for SHA-256 checksum validation.
"""
import hashlib

POKEMON_RED_SHA256 = "5ca7ba01642a3b27b0cc0b5349b52792795b62d3ed977e98a09390659af96b7b"


def compute_sha256(path: str) -> str:
    """
    Compute SHA-256 checksum of a file.

    Args:
        path (str): Path to the file.

    Returns:
        str: SHA-256 checksum as a hex string.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid_pokemon_red_rom(path: str) -> bool:
    """
    Check if the ROM file matches the expected SHA-256 for Pokémon Red.

    Args:
        path (str): Path to the ROM file.

    Returns:
        bool: True if valid, False otherwise.
    """
    return compute_sha256(path) == POKEMON_RED_SHA256
