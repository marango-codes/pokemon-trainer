"""
Gymnasium-compatible environment for Pokémon Red using PyBoy.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from core.emulator import PokemonRedGameWrapper
from core.actions import ALL_ACTIONS, ActionType
from typing import Tuple, Optional, Dict, Any, Union

class PokemonRedEnv(gym.Env):
    """
    Gymnasium environment for Pokémon Red using the PyBoy emulator.

    Provides an interface compliant with Gymnasium API standards (step, reset, etc.)
    to interact with the Pokémon Red game.

    Observation Space: Box(0, 255, (144, 160, 4), uint8) - RGBA screen output.
    Action Space: Discrete(len(ALL_ACTIONS)) - Corresponds to button presses or waiting.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, render_mode: Optional[str] = None) -> None:
        """Initializes the PokemonRedEnv.

        Sets up the emulator, action space, and observation space.

        Args:
            render_mode: The mode for rendering ('human', 'rgb_array', or None).
        """
        super().__init__()

        # Initialize emulator - headless only if not human mode
        self.emu = PokemonRedGameWrapper(headless=(render_mode != 'human'))

        # Define action space (all buttons + wait)
        self.action_space = spaces.Discrete(len(ALL_ACTIONS))

        # Game Boy res (RGBA)
        # Note: Even in human mode, obs comes from emu which is RGBA
        self.observation_space = spaces.Box(0, 255, shape=(144, 160, 4), dtype=np.uint8)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def reset(
        self,
        *,  # Enforce keyword-only arguments after this
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Resets the environment to its initial state.

        Args:
            seed: Optional random seed for the environment.
            options: Optional dictionary of environment-specific options.

        Returns:
            A tuple containing the initial observation (screen pixels) and an info dictionary.
        """
        super().reset(seed=seed)
        self.emu.reset()
        obs = np.array(self.emu.get_screen())
        info = self._get_info()
        return obs, info

    def step(
        self,
        action_idx: int,
        wait_frames: int = 8
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Take an action in the environment using the new emulator interface.

        Args:
            action_idx (int): Index into ALL_ACTIONS (ActionType.KEY_PRESS or WAIT)
            wait_frames (int): Number of frames to wait after input or for wait actions (default 8)

        Returns:
            A tuple containing:
                - obs (np.ndarray): The current screen pixels.
                - reward (float): Reward for the action (currently 0).
                - terminated (bool): Whether the episode has ended.
                - truncated (bool): Whether the episode was truncated.
                - info (dict): Auxiliary information (currently empty).
        """
        action = ALL_ACTIONS[action_idx]
        if action.type == ActionType.KEY_PRESS and action.key is not None:
            self.emu.perform_emulator_action([action.key.value], wait_frames=wait_frames)
        elif action.type == ActionType.WAIT:
            self.emu.perform_emulator_action([], wait_frames=wait_frames)
        obs = np.array(self.emu.get_screen())
        reward = self._calculate_reward() 
        terminated = self._check_terminated() 
        truncated = self._check_truncated() 
        info = self._get_info()

        return obs, reward, terminated, truncated, info

    def render(self) -> Union[np.ndarray, None]:
        """Renders the environment.

        Supports 'rgb_array' mode for returning the screen pixels as a NumPy array
        and 'human' mode for displaying the screen in a PyBoy window.

        Returns:
            NumPy array if mode is 'rgb_array', None otherwise.
        """
        render_mode = self.render_mode  # Get mode from initialized env

        if render_mode == "rgb_array":
            img = np.array(self.emu.get_screen())
            return img
        elif render_mode == "human":
            # PyBoy handles rendering in its own window when headless=False.
            # We just need to tick the emulator to process events and update the display.
            self.emu.pyboy.tick()
            return None # Nothing to return for human mode
        else:
            # Handle other modes if necessary, or rely on superclass
            return super().render()

    def save_state(self, file_path: str) -> None:
        """Saves the current emulator state to a file.

        Args:
            file_path (str): The path to the file where the state will be saved.
        """
        with open(file_path, "wb") as f:
            self.emu.save_state(f)

    def load_state(self, file_path: str) -> None:
        """Loads the emulator state from a file.

        Args:
            file_path (str): The path to the file from which the state will be loaded.
        """
        with open(file_path, "rb") as f:
            self.emu.load_state(f)

    def start_new_game(self) -> bool:
        """Navigates the initial menus to start a new game.

        Uses the underlying emulator's game wrapper functionality.
        This should be called after reset() if not loading a state.

        Returns:
            bool: True if starting the new game was successful, False otherwise.
        """
        self.emu.start_new_game()
        return True

    def close(self) -> None:
        """Cleans up environment resources.

        Closes the emulator and any rendering windows.
        """
        self.emu.close()

    def _get_info(self) -> Dict:
        """Gets relevant game information from the emulator's memory."""
        info = {
            'player_x': self.emu.get_player_x(),
            'player_y': self.emu.get_player_y(),
            'map_id': self.emu.get_current_map_id(),
            'party_count': self.emu.get_party_count(),
            'player_money': self.emu.get_player_money(),
            'rival_name': self.emu.get_rival_name(),
            'player_name': self.emu.get_player_name(),
            'badges': self.emu.get_badges(),
            'pokedex_owned': self.emu.get_pokedex_owned_count(),
            'pokedex_seen': self.emu.get_pokedex_seen_count(),
            'time_played': self.emu.get_time_played(),
            'party_species': self.emu.get_party_species(),
            'party_data': self.emu.get_party_pokemon_data(),
            # Add more game state info here as needed
        }
        return info

    def _calculate_reward(self) -> float:
        """Calculates the reward based on the current game state. Placeholder."""
        # TODO: Implement actual reward logic
        return 0.0

    def _check_terminated(self) -> bool:
        """Checks if the episode has terminated. Placeholder."""
        # TODO: Implement termination conditions (e.g., beat game, blackout)
        return False

    def _check_truncated(self) -> bool:
        """Checks if the episode should be truncated. Placeholder."""
        # TODO: Implement truncation conditions (e.g., step limit)
        return False
