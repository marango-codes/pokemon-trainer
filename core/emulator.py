"""
PyBoy environment loader and interface for Pokemon Red.
"""
from pathlib import Path
from core.rom_utils import is_valid_pokemon_red_rom
from pyboy import PyBoy
from rich.console import Console
from rich.logging import RichHandler
from typing import List, Union
from pyboy.utils import WindowEvent
from PIL.Image import Image
import logging
from io import BytesIO

ROM_PATH = Path(__file__).parent.parent / "roms" / "pokemon_red.gb"

class PokemonRedGameWrapper:
    """Wraps the PyBoy emulator specifically for Pokemon Red,
    providing methods to interact with the game and read specific memory addresses
    to extract game state information.

    Memory addresses are based on known values for Pokemon Red (US/EU).
    Reference: https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_Red_and_Blue/RAM_map
    """
    # Constants for memory addresses (WRAM D000-DFFF range primarily)
    # Player Data
    PLAYER_X_ADDR = 0xD361        # Player's X coordinate on the map
    PLAYER_Y_ADDR = 0xD362        # Player's Y coordinate on the map
    MAP_ID_ADDR = 0xD35E          # Current map ID
    PARTY_COUNT_ADDR = 0xD163     # Number of Pokémon in the party
    MONEY_ADDR = 0xD347           # Player's money (BCD, 3 bytes)
    RIVAL_NAME_ADDR = 0xD34A      # Rival's name (8 bytes)
    PLAYER_NAME_ADDR = 0xD158     # Player's name (7 bytes)
    BADGES_ADDR = 0xD356          # Badges earned (bit flags)
    POKEDEX_OWNED_ADDR = 0xD2F7   # Number of owned Pokémon species (2 bytes, little-endian)
    POKEDEX_SEEN_ADDR = 0xD30A    # Number of seen Pokémon species (2 bytes, little-endian)
    TIME_PLAYED_ADDR = 0xDA40     # Time played (4 bytes, BCD)
    PARTY_SPECIES_LIST_ADDR = 0xD164 # List of species IDs for Pokémon in the party
    PARTY_TERMINATOR = 0xFF       # Terminator for party species list
    PARTY_NICKNAMES_ADDR = 0xD2EC # Start address for the first Pokémon's nickname
    NICKNAME_LENGTH = 11 # Max length of a nickname (10 chars + 1 terminator (0x50))
    POKEMON_DATA_LENGTH = 44 # Size of the data structure for one Pokémon in the party

    def __init__(self, rom_path: str | Path = ROM_PATH, headless: bool = True, log_level=logging.INFO, wait_frames: int = 1, debug: bool = False) -> None:
        """Initializes the emulator and loads the Pokemon Red ROM.

        Args:
            rom_path (str | Path): Path to the ROM file. Defaults to the path defined in ROM_PATH.
            headless (bool): Whether to run in headless ("null" window) mode.
            log_level (int): Logging level for the logger.
            wait_frames (int): Number of frames to wait after each input or for wait actions.
            debug (bool): Enable debug logging.
        """
        # Setup rich logger
        self.console = Console()
        self.logger = logging.getLogger("PokemonRedGameWrapper")
        if not self.logger.hasHandlers():
            handler = RichHandler(console=self.console, markup=True, show_time=True, show_level=True, show_path=False)
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level)
        self.debug = debug

        # Ensure rom_path is a Path object
        rom_path_obj = Path(rom_path)

        if not rom_path_obj.exists():
            self.logger.error(f"ROM not found at {rom_path}. Please place pokemon_red.gb in /roms.")
            raise FileNotFoundError(f"ROM not found at {rom_path}. Please place pokemon_red.gb in /roms.")
        if not is_valid_pokemon_red_rom(rom_path_obj.as_posix()):
            self.logger.error("Invalid ROM: SHA-256 does not match Pokémon Red.")
            raise ValueError("Invalid ROM: SHA-256 does not match Pokémon Red.")
        self.headless = headless
        self.rom_path = rom_path
        self.cgb = False

        # Branch logic for window backend, sound emulation, and speed
        if self.headless:
            window_mode = "null"
            sound_emulated = False
        else:
            window_mode = "SDL2"  # Default to SDL2 for interactive/human play
            sound_emulated = True
        self.logger.info(f"Initializing PyBoy: window={window_mode}, sound_emulated={sound_emulated}, cgb={self.cgb}, headless={headless}")

        self.pyboy = PyBoy(
            gamerom=rom_path_obj.as_posix(),
            window=window_mode,
            sound_emulated=sound_emulated,
            cgb=self.cgb
        )

        # Set emulation speed: 0 (unlimited) for headless, 5 for interactive
        self.pyboy.set_emulation_speed(0 if self.headless else 5)
        self.logger.debug(f"Emulation speed set to {'unlimited' if self.headless else '5x'}.")

    def reset(self) -> None:
        """Reset the emulator to the initial state.
        Stops the current emulation (without saving) and re-initializes PyBoy.
        """
        self.logger.info("Resetting emulator...")
        self.pyboy.stop(save=False)
        if self.headless:
            window_mode = "null"
            sound_emulated = False
        else:
            window_mode = "SDL2"
            sound_emulated = True
        self.logger.debug(f"Reset PyBoy: window={window_mode}, sound_emulated={sound_emulated}, cgb={self.cgb}, headless={self.headless}")

        self.pyboy = PyBoy(
            gamerom=self.rom_path.as_posix(),
            window=window_mode,
            sound_emulated=sound_emulated,
            cgb=self.cgb
        )

        self.pyboy.set_emulation_speed(0 if self.headless else 5)
        self.logger.debug(f"Emulation speed set to {'unlimited' if self.headless else '5x'} after reset.")

    def perform_emulator_action(self, button_presses: List[Union[str, WindowEvent]], wait_frames: int = 8) -> None:
        """Perform a sequence of button presses on the emulator.
        Each button in the list is pressed (pyboy.button), then the emulator advances by wait_frames ticks.
        If button_presses is empty, this is a wait action and the emulator simply ticks for wait_frames.

        Args:
            button_presses (List[Union[str, WindowEvent]]): List of button names (PyBoy-compatible) to press.
            wait_frames (int): Number of frames to wait after each input or for wait actions.
        """
        if self.debug:
            # Use WindowEvent names if they exist, otherwise use the raw value
            button_names = [btn.name if isinstance(btn, WindowEvent) else str(btn) for btn in button_presses]
            self.logger.debug(f"Performing emulator action: button_presses={button_names}, wait_frames={wait_frames}")
        if not button_presses:
            self.pyboy.tick(wait_frames)
        else:
            for btn in button_presses:
                self.pyboy.button(btn)
                self.pyboy.tick(wait_frames)

    def get_screen(self) -> Image:
        """Gets the current screen image from the emulator.

        Returns:
            PIL.Image.Image: The current screen content as a PIL Image.
        """
        return self.pyboy.screen.image

    def start_new_game(self) -> bool:
        """Manually navigates the menus to start a new game.

        Sends button presses and ticks to get past the title screen and select 'NEW GAME'.

        Returns:
            bool: True (assumes success if sequence completes).
        """
        self.logger.info("Attempting to automatically start a new game...")
        # Sequence: Press START at title screen -> wait -> Press A at main menu -> wait
        try:
            self.logger.debug("Pressing START at title screen...")
            self.pyboy.button(WindowEvent.PRESS_BUTTON_START)
            self.pyboy.tick(60) # Wait ~1 second

            self.logger.debug("Pressing A at main menu (select NEW GAME)...")
            self.pyboy.button(WindowEvent.PRESS_BUTTON_A)
            self.pyboy.tick(60) # Wait ~1 second

            # Add more ticks to allow the game to transition past the menu
            self.pyboy.tick(120) # Wait ~2 more seconds

            self.logger.info("New game started via manual input sequence.")
            return True
        except Exception as e:
            self.logger.error(f"Error during manual start sequence: {e}")
            return False

    # --- Memory Reading Methods ---
    def get_memory_value(self, addr: int) -> int:
        """Gets a single byte value from a specific memory address."""
        return self.pyboy.memory[addr] # In PyBoy, memory is directly accessible

    def get_player_x(self) -> int:
        """Reads the player's X coordinate from RAM (0xD361)."""
        return self.get_memory_value(self.PLAYER_X_ADDR)

    def get_player_y(self) -> int:
        """Reads the player's Y coordinate from RAM (0xD362)."""
        return self.get_memory_value(self.PLAYER_Y_ADDR)

    def get_player_coords(self) -> tuple[int, int]:
        """Reads the player's X and Y coordinates from RAM."""
        return self.get_player_x(), self.get_player_y()

    def get_current_map_id(self) -> int:
        """Reads the current map ID from RAM (0xD35E)."""
        return self.get_memory_value(self.MAP_ID_ADDR)

    def get_party_count(self) -> int:
        """Reads the number of Pokémon currently in the player's party (0xD163)."""
        count = self.get_memory_value(self.PARTY_COUNT_ADDR)
        return count

    def get_player_money(self) -> int:
        """Reads the player's money from RAM (0xD347-0xD349).
        Money is stored in Binary-Coded Decimal (BCD) format.
        """
        # Read the 3 bytes representing money in BCD
        bcd1 = self.get_memory_value(self.MONEY_ADDR)
        bcd2 = self.get_memory_value(self.MONEY_ADDR + 1)
        bcd3 = self.get_memory_value(self.MONEY_ADDR + 2)
        # Decode each byte from BCD to integer and combine
        return self._decode_bcd(bcd1) * 10000 + self._decode_bcd(bcd2) * 100 + self._decode_bcd(bcd3)

    def get_rival_name(self) -> str:
        """Reads the rival's name from memory (max 7 characters)."""
        name_bytes = []
        max_len = 7 # Max 7 chars
        for i in range(max_len): # Read up to max_len characters
            byte = self.get_memory_value(self.RIVAL_NAME_ADDR + i)
            if byte == 0x50: # Terminator character
                break
            name_bytes.append(byte)
        # Ensure the byte after the potential name is checked for terminator only if loop didn't break
        # The original code read one byte too many if the name was exactly max_len
        return self._decode_text(name_bytes)

    def get_player_name(self) -> str:
        """Reads the player's name from memory (max 7 characters)."""
        name_bytes = []
        max_len = 7 # Max 7 chars
        for i in range(max_len): # Read up to max_len characters
            byte = self.get_memory_value(self.PLAYER_NAME_ADDR + i)
            if byte == 0x50: # Terminator character
                break
            name_bytes.append(byte)
        # Ensure the byte after the potential name is checked for terminator only if loop didn't break
        return self._decode_text(name_bytes)

    def get_badges(self) -> int:
        """Reads the player's badges from RAM (0xD356).
        Each bit corresponds to a badge:
        Bit 0: Boulder Badge (Brock)
        ...
        """
        return self.get_memory_value(self.BADGES_ADDR)

    def get_pokedex_owned_count(self) -> int:
        """Reads the number of owned Pokémon species from RAM (0xD2F7-0xD2F8).
        This seems to be a simple count, not derived from flags.
        Stored as a 2-byte little-endian integer.
        """
        lsb = self.get_memory_value(self.POKEDEX_OWNED_ADDR)
        msb = self.get_memory_value(self.POKEDEX_OWNED_ADDR + 1)
        # Combine LSB and MSB (Little-Endian)
        return lsb + (msb * 256)

    def get_pokedex_seen_count(self) -> int:
        """Reads the number of seen Pokémon species from RAM (0xD30A-0xD30B).
        Stored as a 2-byte little-endian integer.
        """
        lsb = self.get_memory_value(self.POKEDEX_SEEN_ADDR)
        msb = self.get_memory_value(self.POKEDEX_SEEN_ADDR + 1)
        # Combine LSB and MSB (Little-Endian)
        return lsb + (msb * 256)

    def get_time_played(self) -> tuple[int, int, int, int]:
        """Reads the time played from RAM (0xDA40 - 0xDA43).
        The time is stored as separate bytes for hours, minutes, seconds, and frames,
        each encoded in Binary-Coded Decimal (BCD).

        Returns:
            tuple[int, int, int, int]: (hours, minutes, seconds, frames).
        """
        hours   = self._decode_bcd(self.get_memory_value(self.TIME_PLAYED_ADDR))
        minutes = self._decode_bcd(self.get_memory_value(self.TIME_PLAYED_ADDR + 1))
        seconds = self._decode_bcd(self.get_memory_value(self.TIME_PLAYED_ADDR + 2))
        frames  = self._decode_bcd(self.get_memory_value(self.TIME_PLAYED_ADDR + 3))
        return hours, minutes, seconds, frames

    def get_party_species(self) -> list[int]:
        """Reads the list of species IDs for Pokémon currently in the player's party.
        Reads from RAM starting at 0xD164, terminated by 0xFF.

        Returns:
            list[int]: A list of species IDs (internal game values).
        """
        party_count = self.get_party_count()
        if party_count == 0:
            return []

        species_list = []
        current_addr = self.PARTY_SPECIES_LIST_ADDR # Start at 0xD164

        # The list is terminated by 0xFF, read up to 'party_count' entries before terminator
        for _ in range(party_count):
            species_id = self.get_memory_value(current_addr)
            if species_id == self.PARTY_TERMINATOR: # Check for terminator 0xFF
                break # Stop if terminator is encountered before party_count is reached
            species_list.append(species_id)
            current_addr += 1

        # Simple check for the terminator immediately after the expected number of Pokémon
        if self.get_memory_value(self.PARTY_SPECIES_LIST_ADDR + party_count) != self.PARTY_TERMINATOR:
             logging.warning(f"Party species list terminator 0xFF not found at expected position: {self.PARTY_SPECIES_LIST_ADDR + party_count:X}")

        return species_list

    def get_party_pokemon_nicknames(self) -> list[str]:
        """Reads the nicknames of all Pokémon currently in the player's party.

        Iterates through the party based on the count obtained from get_party_count().
        For each Pokémon, it reads bytes from the corresponding nickname slot
        starting at PARTY_NICKNAMES_ADDR (0xD2EC), up to NICKNAME_LENGTH (11 bytes).
        Reading stops early if the terminator character (0x50) is encountered.
        The collected bytes are then decoded into a string.

        Returns:
            list[str]: A list of nickname strings for each Pokémon in the party.
        """
        party_count = self.get_party_count()
        nicknames = []
        for i in range(party_count):
            start_addr = self.PARTY_NICKNAMES_ADDR + i * self.NICKNAME_LENGTH
            name_bytes = []
            for j in range(self.NICKNAME_LENGTH):
                byte = self.get_memory_value(start_addr + j)
                if byte == 0x50: # Terminator character
                    break
                name_bytes.append(byte)
            nicknames.append(self._decode_text(name_bytes))
        return nicknames

    def get_party_pokemon_data(self) -> list[dict]:
        """Reads detailed data for each Pokémon in the party.
        Iterates through the number of Pokémon specified by `get_party_count()` (0xD163).
        Reads a 44-byte data structure for each Pokémon starting from the base address 0xD16B.
        The structure contains information like species ID, HP, stats, EVs, IVs, moves, PP, etc.

        Returns:
            list[dict]: A list where each dictionary represents a Pokémon in the party.
                        Returns an empty list if the party is empty.
        """
        party_count = self.get_party_count()
        if party_count == 0:
            return []

        pokemon_data_list = []
        base_addr = 0xD16B
        pokemon_struct_size = 44 # 0x2C bytes

        for i in range(party_count):
            start_addr = base_addr + i * pokemon_struct_size
            pokemon_info = {}

            # Basic Info
            pokemon_info['species_id'] = self.get_memory_value(start_addr + 0x00)
            pokemon_info['current_hp'] = self._read_little_endian(start_addr + 0x01, 2)
            pokemon_info['status'] = self.get_memory_value(start_addr + 0x04)
            pokemon_info['type1'] = self.get_memory_value(start_addr + 0x05)
            pokemon_info['type2'] = self.get_memory_value(start_addr + 0x06)
            pokemon_info['level'] = self.get_memory_value(start_addr + 0x21) # Actual level

            # Moves & PP
            pokemon_info['moves'] = [
                self.get_memory_value(start_addr + 0x08),
                self.get_memory_value(start_addr + 0x09),
                self.get_memory_value(start_addr + 0x0A),
                self.get_memory_value(start_addr + 0x0B)
            ]
            pokemon_info['pp'] = [
                self.get_memory_value(start_addr + 0x1D),
                self.get_memory_value(start_addr + 0x1E),
                self.get_memory_value(start_addr + 0x1F),
                self.get_memory_value(start_addr + 0x20)
            ]

            # Trainer & Exp
            pokemon_info['trainer_id'] = self._read_little_endian(start_addr + 0x0C, 2)
            pokemon_info['exp'] = self._read_little_endian(start_addr + 0x0E, 3)

            # EVs
            pokemon_info['evs'] = {
                'hp': self._read_little_endian(start_addr + 0x11, 2),
                'attack': self._read_little_endian(start_addr + 0x13, 2),
                'defense': self._read_little_endian(start_addr + 0x15, 2),
                'speed': self._read_little_endian(start_addr + 0x17, 2),
                'special': self._read_little_endian(start_addr + 0x19, 2),
            }

            # IVs
            iv_byte1 = self.get_memory_value(start_addr + 0x1B)
            iv_byte2 = self.get_memory_value(start_addr + 0x1C)
            pokemon_info['ivs'] = self._extract_ivs(iv_byte1, iv_byte2)

            # Stats
            pokemon_info['stats'] = {
                'max_hp': self._read_little_endian(start_addr + 0x22, 2),
                'attack': self._read_little_endian(start_addr + 0x24, 2),
                'defense': self._read_little_endian(start_addr + 0x26, 2),
                'speed': self._read_little_endian(start_addr + 0x28, 2),
                'special': self._read_little_endian(start_addr + 0x2A, 2),
            }

            pokemon_data_list.append(pokemon_info)

        return pokemon_data_list

    # --- Helper Methods ---
    def _read_little_endian(self, start_addr: int, num_bytes: int) -> int:
        """Reads `num_bytes` starting from `start_addr` and interprets them
        as a little-endian integer.

        Little-endian means the least significant byte is stored at the lowest memory address.
        This is standard for the Game Boy's Z80-like processor.

        Example: Reading 0x1234 stored at 0xC000:
            Memory[0xC000] = 0x34 (LSB)
            Memory[0xC001] = 0x12 (MSB)
            Result = (0x12 << 8) | 0x34 = 0x1234
        """
        value = 0
        for i in range(num_bytes):
            byte_val = self.get_memory_value(start_addr + i)
            value += byte_val << (8 * i)
        return value

    def _extract_ivs(self, iv_byte1: int, iv_byte2: int) -> dict[str, int]:
        """Extracts Individual Values (IVs) from the two bytes used to store them in Gen 1.

        IVs determine a Pokémon's stat potential and range from 0-15 for each stat.
        In Gen 1, they are packed as follows:
        - Byte 1: Attack (high nibble), Defense (low nibble)
        - Byte 2: Speed (high nibble), Special (low nibble)
        The HP IV is derived from the least significant bits of the other four IVs.
        """
        attack_iv = (iv_byte1 >> 4) & 0x0F
        defense_iv = iv_byte1 & 0x0F
        speed_iv = (iv_byte2 >> 4) & 0x0F
        special_iv = iv_byte2 & 0x0F
        # HP IV calculation: (Atk LSB << 3) | (Def LSB << 2) | (Spd LSB << 1) | (Spc LSB << 0)
        hp_iv = ((attack_iv & 1) << 3) | ((defense_iv & 1) << 2) | ((speed_iv & 1) << 1) | (special_iv & 1)
        return {'hp': hp_iv, 'attack': attack_iv, 'defense': defense_iv, 'speed': speed_iv, 'special': special_iv}

    def _decode_text(self, byte_list: List[int]) -> str:
        """Decodes a list of bytes using the Pokemon Gen 1 custom text encoding.

        Gen 1 games use a non-standard character set. This function maps the
        byte values found in RAM to their corresponding printable characters.
        The terminator character (0x50) is mapped to an empty string.

        Mapping Reference: https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_Red_and_Blue/Text_data
        (Note: The exact mapping might vary slightly based on source, using a common one here)
        """
        POKEMON_CHARS = {
            0x50: "",  # Terminator character
            0x7F: " ", 0x80: "A", 0x81: "B", 0x82: "C", 0x83: "D", 0x84: "E", 0x85: "F",
            0x86: "G", 0x87: "H", 0x88: "I", 0x89: "J", 0x8A: "K", 0x8B: "L", 0x8C: "M",
            0x8D: "N", 0x8E: "O", 0x8F: "P", 0x90: "Q", 0x91: "R", 0x92: "S", 0x93: "T",
            0x94: "U", 0x95: "V", 0x96: "W", 0x97: "X", 0x98: "Y", 0x99: "Z",
            0xA0: "a", 0xA1: "b", 0xA2: "c", 0xA3: "d", 0xA4: "e", 0xA5: "f",
            0xA6: "g", 0xA7: "h", 0xA8: "i", 0xA9: "j", 0xAA: "k", 0xAB: "l", 0xAC: "m",
            0xAD: "n", 0xAE: "o", 0xAF: "p", 0xB0: "q", 0xB1: "r", 0xB2: "s", 0xB3: "t",
            0xB4: "u", 0xB5: "v", 0xB6: "w", 0xB7: "x", 0xB8: "y", 0xB9: "z",
            0xF6: "0", 0xF7: "1", 0xF8: "2", 0xF9: "3", 0xFA: "4", 0xFB: "5", 0xFC: "6",
            0xFD: "7", 0xFE: "8", 0xFF: "9",
            # Add other characters as needed (e.g., punctuation, symbols)
        }
        return "".join(POKEMON_CHARS.get(byte, "?") for byte in byte_list) # Use '?' for unknown chars

    def _decode_bcd(self, bcd_value: int) -> int:
        """Decodes a Binary-Coded Decimal value."""
        # BCD represents decimal digits (0-9) using 4 bits per digit.
        # A single byte can store two BCD digits (e.g., 0x21 represents decimal 21).
        # Example: bcd_value = 0x59 (binary 0101 1001)
        #   high_nibble = (0x59 >> 4) = 0x05
        #   low_nibble = 0x59 & 0x0F = 0x09
        #   Result = (high_nibble * 10) + low_nibble = (5 * 10) + 9 = 59
        high_nibble = (bcd_value >> 4) & 0x0F
        low_nibble = bcd_value & 0x0F
        # Ensure nibbles are valid BCD digits (0-9)
        if high_nibble > 9 or low_nibble > 9:
            logging.warning(f"Invalid BCD byte encountered: {bcd_value:X}")
            # Handle error appropriately, e.g., return 0 or raise exception
            # Returning 0 for now to avoid breaking reads like time/money
            return 0 # Or potentially: high_nibble * 10 + low_nibble anyway?
        return high_nibble * 10 + low_nibble

    # --- Game Interaction Methods ---
    def run_action_on_emulator(self, action: int) -> None:
        """Runs an action on the emulator.

        Args:
            action (int): The action to run.
        """
        self.pyboy.button(action)

    def save_state(self, file: BytesIO) -> None:
        """Saves the current state of the emulator to a file-like object.

        Args:
            file (BytesIO): A writable, binary file-like object (e.g., open('state.sav', 'wb')).
        """
        self.pyboy.save_state(file)

    def load_state(self, file: BytesIO) -> None:
        """Loads the emulator state from a file-like object.

        Args:
            file (BytesIO): A readable, binary file-like object (e.g., open('state.sav', 'rb')).
        """
        self.pyboy.load_state(file)

    def close(self) -> None:
        """Stops the emulator without saving."""
        self.pyboy.stop(save=False)