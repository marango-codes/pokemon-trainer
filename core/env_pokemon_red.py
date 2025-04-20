"""
Gymnasium-compatible environment for Pokémon Red using PyBoy.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from core.emulator import PokemonRedGameWrapper
from core.actions import ALL_ACTIONS, ActionType

class PokemonRedEnv(gym.Env):
    """
    Gymnasium environment for Pokémon Red.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self):
        super().__init__()
        self.emu = PokemonRedGameWrapper()
        self.action_space = spaces.Discrete(len(ALL_ACTIONS))
        self.observation_space = spaces.Box(0, 255, shape=(144, 160, 3), dtype=np.uint8)  # Game Boy res

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.emu.reset()
        obs = np.array(self.emu.get_screen())
        info = {}
        return obs, info

    def step(self, action_idx, wait_frames: int = 8):
        """
        Take an action in the environment using the new emulator interface.
        Args:
            action_idx (int): Index into ALL_ACTIONS (ActionType.KEY_PRESS or WAIT)
            wait_frames (int): Number of frames to wait after input or for wait actions (default 8)
        Returns:
            obs, reward, terminated, truncated, info
        """
        action = ALL_ACTIONS[action_idx]
        if action.type == ActionType.KEY_PRESS and action.key is not None:
            self.emu.perform_emulator_action([action.key.value], wait_frames=wait_frames)
        elif action.type == ActionType.WAIT:
            self.emu.perform_emulator_action([], wait_frames=wait_frames)
        obs = np.array(self.emu.get_screen())
        reward = 0  # TODO: Define reward function
        terminated = False  # TODO: Set proper termination
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info

    def render(self, mode="human"):
        img = np.array(self.emu.get_screen())
        if mode == "rgb_array":
            return img
        elif mode == "human":
            import matplotlib.pyplot as plt
            plt.imshow(img)
            plt.show()

    def close(self):
        self.emu.close()
