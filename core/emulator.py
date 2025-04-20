"""
PyBoy environment loader and interface for Pokemon Red.
"""
from pathlib import Path
from core.rom_utils import is_valid_pokemon_red_rom
from pyboy import PyBoy

ROM_PATH = Path(__file__).parent.parent / "roms" / "pokemon_red.gb"

class PyBoyEnv:
    """
    Loads and manages a PyBoy emulator instance for Pokemon Red.
    """
    def __init__(self, rom_path: Path = ROM_PATH, headless: bool = True):
        """
        Initialize the PyBoy emulator for Pokemon Red.

        Args:
            rom_path (Path): Path to the ROM file.
            headless (bool): Whether to run in headless ("null" window) mode.
        """
        if not rom_path.exists():
            raise FileNotFoundError(f"ROM not found at {rom_path}. Please place pokemon_red.gb in /roms.")
        # Always use as_posix() for cross-platform compatibility
        if not is_valid_pokemon_red_rom(rom_path.as_posix()):
            raise ValueError("Invalid ROM: SHA-256 does not match Pokémon Red.")
        window_mode = "null" if headless else "SDL2"
        self.pyboy = PyBoy(rom_path.as_posix(), window=window_mode)
        self.headless = headless
        self.rom_path = rom_path

    def reset(self):
        """
        Reset the emulator to the initial state.
        """
        self.pyboy.stop(save=False)
        window_mode = "null" if self.headless else "SDL2"
        self.pyboy = PyBoy(self.rom_path.as_posix(), window=window_mode)

    def step(self, button_presses):
        # button_presses: list of PyBoy button enums
        for btn in button_presses:
            self.pyboy.send_input(btn)
        self.pyboy.tick()

    def get_screen(self):
        return self.pyboy.screen.image

    def close(self):
        self.pyboy.stop(save=False)
