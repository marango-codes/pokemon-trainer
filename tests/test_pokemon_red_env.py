"""
Unit tests for core.pokemon_red_env (Gymnasium-compatible env).
"""
import pytest
from core.env_pokemon_red import PokemonRedEnv
from core.emulator import ROM_PATH
import numpy as np

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_env_reset_expected():
    """
    Test that the environment can be reset and returns (obs, info) tuple.
    """
    env = PokemonRedEnv()
    result = env.reset()
    assert isinstance(result, tuple), "reset() should return a tuple"
    assert len(result) == 2, "reset() should return (obs, info)"
    obs, info = result
    assert isinstance(obs, np.ndarray)
    assert isinstance(info, dict)
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_env_step_and_render():
    """
    Test that the environment step returns the correct tuple and rendering works.
    """
    env = PokemonRedEnv()
    obs, info = env.reset()
    for i in range(env.action_space.n):
        result = env.step(i, wait_frames=4)
        assert isinstance(result, tuple), "step() should return a tuple"
        assert len(result) == 5, "step() should return (obs, reward, terminated, truncated, info)"
        obs2, reward, terminated, truncated, info2 = result
        assert isinstance(obs2, np.ndarray)
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info2, dict)
    env.render(mode="rgb_array")
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_env_step_custom_wait():
    """
    Test that custom wait_frames parameter works.
    """
    env = PokemonRedEnv()
    obs, info = env.reset()
    result = env.step(0, wait_frames=16)  # Use a valid action index and a large wait
    obs2, reward, terminated, truncated, info2 = result
    assert isinstance(obs2, np.ndarray)
    env.close()
