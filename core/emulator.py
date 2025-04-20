"""
PyBoy environment loader and interface for Pokemon Red.
"""
from pathlib import Path
from core.rom_utils import is_valid_pokemon_red_rom
from pyboy import PyBoy
from rich.console import Console
from rich.logging import RichHandler
import logging

ROM_PATH = Path(__file__).parent.parent / "roms" / "pokemon_red.gb"

class PokemonRedGameWrapper:
    """
    Loads and manages a PyBoy emulator instance for Pokemon Red.
    Handles headless/interactive mode, sound, OpenGL/SDL2, and emulation speed.
    """
    def __init__(self, rom_path: Path = ROM_PATH, headless: bool = True, cgb: bool = False, debug: bool = False):
        """
        Initialize the PyBoy emulator for Pokemon Red.

        Args:
            rom_path (Path): Path to the ROM file.
            headless (bool): Whether to run in headless ("null" window) mode.
            cgb (bool): Force CGB (Color Game Boy) mode if True.
            debug (bool): Enable debug logging.
        """
        # Setup rich logger
        self.console = Console()
        self.logger = logging.getLogger("PokemonRedGameWrapper")
        if not self.logger.hasHandlers():
            handler = RichHandler(console=self.console, markup=True, show_time=True, show_level=True, show_path=False)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.debug = debug

        if not rom_path.exists():
            self.logger.error(f"ROM not found at {rom_path}. Please place pokemon_red.gb in /roms.")
            raise FileNotFoundError(f"ROM not found at {rom_path}. Please place pokemon_red.gb in /roms.")
        if not is_valid_pokemon_red_rom(rom_path.as_posix()):
            self.logger.error("Invalid ROM: SHA-256 does not match Pokémon Red.")
            raise ValueError("Invalid ROM: SHA-256 does not match Pokémon Red.")
        self.headless = headless
        self.rom_path = rom_path
        self.cgb = cgb

        # Branch logic for window backend, sound, and emulation speed
        if self.headless:
            window_mode = "null"
            sound = False
        else:
            window_mode = "SDL2"  # Default to SDL2 for interactive/human play
            sound = True
        self.logger.info(f"Initializing PyBoy: window={window_mode}, sound={sound}, cgb={cgb}, headless={headless}")
        self.pyboy = PyBoy(
            gamerom=rom_path.as_posix(),
            window=window_mode,
            sound=sound,
            cgb=cgb
        )
        # Set emulation speed: 0 (unlimited) for headless, 5 for interactive
        self.pyboy.set_emulation_speed(0 if self.headless else 5)
        self.logger.debug(f"Emulation speed set to {'unlimited' if self.headless else '5x'}.")

    def reset(self):
        """
        Reset the emulator to the initial state.
        """
        self.logger.info("Resetting emulator...")
        self.pyboy.stop(save=False)
        if self.headless:
            window_mode = "null"
            sound = False
        else:
            window_mode = "SDL2"
            sound = True
        self.logger.debug(f"Reset PyBoy: window={window_mode}, sound={sound}, cgb={self.cgb}, headless={self.headless}")
        self.pyboy = PyBoy(
            gamerom=self.rom_path.as_posix(),
            window=window_mode,
            sound=sound,
            cgb=self.cgb
        )
        self.pyboy.set_emulation_speed(0 if self.headless else 5)
        self.logger.debug(f"Emulation speed set to {'unlimited' if self.headless else '5x'} after reset.")

    def perform_emulator_action(self, button_presses: list, wait_frames: int = 8):
        """
        Perform a sequence of button presses on the emulator.
        Each button in the list is pressed (pyboy.button), then the emulator advances by wait_frames ticks.
        If button_presses is empty, this is a wait action and the emulator simply ticks for wait_frames.

        Args:
            button_presses (list[str|enum]): List of button names (PyBoy-compatible) to press.
            wait_frames (int): Number of frames to wait after each input or for wait actions.
        """
        if self.debug:
            self.logger.debug(f"Performing emulator action: button_presses={button_presses}, wait_frames={wait_frames}")
        if not button_presses:
            self.pyboy.tick(wait_frames)
        else:
            for btn in button_presses:
                self.pyboy.button(btn)
                self.pyboy.tick(wait_frames)

    def get_screen(self):
        return self.pyboy.screen.image

    def close(self):
        self.pyboy.stop(save=False)