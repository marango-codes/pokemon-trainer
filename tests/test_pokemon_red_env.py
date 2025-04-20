"""
Unit tests for core.pokemon_red_env (Gymnasium-compatible env).
"""
import pytest
from core.env_pokemon_red import PokemonRedEnv
from core.emulator import ROM_PATH

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_env_reset_expected():
    env = PokemonRedEnv()
    obs, info = env.reset()
    assert obs is not None
    env.close()

@pytest.mark.skipif(not ROM_PATH.exists(), reason="pokemon_red.gb ROM not present")
def test_env_step_and_render():
    env = PokemonRedEnv()
    obs, info = env.reset()
    # Test all actions in the discrete space (smoke test)
    for i in range(env.action_space.n):
        obs2, reward, terminated, truncated, info2 = env.step(i)
        assert obs2 is not None
    env.render(mode="rgb_array")
    env.close()
