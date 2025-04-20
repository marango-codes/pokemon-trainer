"""
Gymnasium-compatible environment for Pokémon Red using PyBoy.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from core.emulator import PyBoyEnv
from core.actions import ALL_ACTIONS, ActionType, KEY_TO_EVENTS

class PokemonRedEnv(gym.Env):
    """
    Gymnasium environment for Pokémon Red.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self):
        super().__init__()
        self.emu = PyBoyEnv()
        self.action_space = spaces.Discrete(len(ALL_ACTIONS))
        self.observation_space = spaces.Box(0, 255, shape=(144, 160, 3), dtype=np.uint8)  # Game Boy res

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.emu.reset()
        obs = np.array(self.emu.get_screen())
        info = {}
        return obs, info

    def step(self, action_idx):
        action = ALL_ACTIONS[action_idx]
        if action.type == ActionType.KEY_PRESS and action.key is not None:
            press, release = KEY_TO_EVENTS[action.key]
            self.emu.step([press])
            self.emu.step([release])
        elif action.type == ActionType.WAIT:
            self.emu.step([])  # Advance one frame with no input
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
