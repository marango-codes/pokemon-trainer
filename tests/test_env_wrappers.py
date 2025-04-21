import pytest
import numpy as np
from core.env_wrappers import make_pokemon_red_env
from core.emulator import ROM_PATH

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_wrapped_env_shape_and_reset_step():
    # Use a small shape and stack to speed test
    shape = (32, 32)
    num_stack = 4
    env = make_pokemon_red_env(mode="rl", shape=shape, num_stack=num_stack)
    # Observation space reflects wrappers: (num_stack, H, W, 1)
    assert env.observation_space.shape == (num_stack, shape[0], shape[1], 1)

    # reset() returns (obs, info)
    obs, info = env.reset()
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (num_stack, shape[0], shape[1], 1)
    assert isinstance(info, dict)

    # step() returns (obs, reward, terminated, truncated, info)
    result = env.step(0)
    assert isinstance(result, tuple) and len(result) == 5
    obs2, reward, terminated, truncated, info2 = result
    assert isinstance(obs2, np.ndarray) and obs2.shape == obs.shape
    assert isinstance(reward, (int, float))
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert isinstance(info2, dict)

    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_default_wrapper_settings():
    # Default settings: shape=(84,84), num_stack=4
    env = make_pokemon_red_env()
    obs, _ = env.reset()
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (4, 84, 84, 1)
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_llm_mode_resize_only():
    # LLm mode: resize but keep full-color, no stacking
    shape = (32, 32)
    env = make_pokemon_red_env(mode="llm", shape=shape)
    obs, info = env.reset()
    assert isinstance(obs, np.ndarray)
    # Expect single frame, color channels (RGB)
    assert obs.shape == (shape[0], shape[1], 3)
    assert isinstance(info, dict)
    obs2, reward, terminated, truncated, info2 = env.step(0)
    assert isinstance(obs2, np.ndarray) and obs2.shape == obs.shape
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_human_mode_native():
    # Human mode: native full-resolution RGB
    env = make_pokemon_red_env(mode="human")
    obs, info = env.reset()
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (144, 160, 3)
    obs2, *_ = env.step(0)
    assert isinstance(obs2, np.ndarray) and obs2.shape == obs.shape
    env.close()
