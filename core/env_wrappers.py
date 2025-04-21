"""Module to provide wrapped Gymnasium environments for RL/LLM agents.

This wrapper applies standard RL preprocessing:
1. ResizeObservation: downsample native 144×160 RGB to a smaller `shape`.
2. GrayScaleObservation: convert to single-channel grayscale.
3. FrameStack: stack the last `num_stack` frames to encode temporal context.

This setup optimizes input dimensionality and training speed. It’s intended
for RL/LLM agents—if you need a human-friendly, full-color 144×160 view, use
`PokemonRedEnv` from `core.env_pokemon_red` directly."""
from typing import Tuple, Literal
import gymnasium as gym
from core.env_pokemon_red import PokemonRedEnv
from gymnasium.wrappers import ResizeObservation, GrayscaleObservation, FrameStackObservation

from gymnasium import ObservationWrapper
from gymnasium.spaces import Box
import numpy as np

class DropAlpha(ObservationWrapper):
    """Drop the alpha channel from an RGBA observation, yielding RGB."""
    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        obs_space = env.observation_space
        if not (len(obs_space.shape) == 3 and obs_space.shape[-1] == 4):
             raise ValueError(f"DropAlpha expects a 3D observation space with 4 channels (RGBA), got {obs_space.shape}")
        # Keep only first 3 channels
        low = obs_space.low[..., :3]
        high = obs_space.high[..., :3]
        self.observation_space = Box(low=low, high=high, dtype=obs_space.dtype)

    def observation(self, obs: np.ndarray) -> np.ndarray:
        # Drop alpha channel
        return obs[..., :3]

def make_pokemon_red_env(
    mode: Literal["rl", "llm", "human"] = "rl",
    shape: Tuple[int, int] = (84, 84),
    num_stack: int = 4,
) -> gym.Env:
    """
    Create a PokemonRedEnv pipeline for RL/LLM/human use.

    Modes:
      - "rl": Resize -> Drop Alpha -> GrayScale -> FrameStack
      - "llm": Resize -> Drop Alpha (keep color, no stacking)
      - "human": Drop Alpha (native resolution, RGB)

    Args:
        mode: which pipeline to apply ("rl", "llm", or "human").
        shape: (height, width) for resizing in 'rl'/'llm' modes.
        num_stack: number of frames to stack (only in 'rl' mode).

    Returns:
        A `gym.Env` ready for the specified mode.
    """
    env = PokemonRedEnv()
    if mode == "rl":
        # RL: Resize -> Drop Alpha -> GrayScale -> FrameStack
        env = ResizeObservation(env, shape)
        env = DropAlpha(env)
        env = GrayscaleObservation(env, keep_dim=True)
        env = FrameStackObservation(env, stack_size=num_stack)
    elif mode == "llm":
        # LLM: Resize -> Drop Alpha (keep color, no stack)
        env = ResizeObservation(env, shape)
        env = DropAlpha(env)
    elif mode == "human":
        # Human: Drop Alpha (native resolution, RGB)
        env = DropAlpha(env)
    else:
        raise ValueError(f"Unknown mode {mode!r}, must be 'rl', 'llm', or 'human'")
    return env
