# pokemon-trainer

A unified Python framework that lets RL agents, LLM agents, or humans play Pokémon Red interchangeably while spectators can watch in real time or replay.

## Project Overview
- **Modular, agent-agnostic design:** RL, LLM, and human agents can play interchangeably.
- **Spectator support:** Real-time and replayable viewing via CLI or windowed UI.
- **FastAPI bridge:** For remote agent and spectator connections (REST & WebSocket).
- **Deterministic, testable, and reproducible:** Gymnasium environment, pytest, and ruff for quality.

## Directory Structure
```
/pokemon-trainer/
  /agents/         # RL, LLM, and human agent wrappers
  /core/           # Game interface (emulator), actions, environment, session manager, pydantic models
  /api/            # FastAPI endpoints for agent and spectator control
  /replay/         # Replay storage, playback, and utilities
  /tests/          # Pytest suites mirroring above structure
  README.md
  PLANNING.md
  TASK.md
  pyproject.toml
```

## Getting Started
1. **Install dependencies** (requires Python 3.11+):
   ```sh
   uv pip install
   ```
2. **Place your Pokémon Red ROM** as `roms/pokemon_red.gb` (create the `/roms/` directory if it does not exist).
   - The project will automatically validate the ROM using its SHA-256 checksum.
   - If the ROM is invalid, you will be notified and the emulator will not start.
   - **How to obtain the ROM legally:** You must dump the ROM from a cartridge you own, using legal tools/hardware. This project does not distribute, endorse, or condone piracy of copyrighted ROMs.
   - For more information on legal ROM dumping, see [Dumping Game Boy cartridges](https://retrostuff.org/2019/09/22/dumping-game-boy-cartridges/).
3. **Run tests:**
   ```sh
   pytest
   ```

## Usage
- RL agent: see `agents/rl_agent.py`
- LLM agent: see `agents/llm_agent.py` and API docs in `api/server.py`
- Human: see `agents/human_agent.py`
- Spectator: CLI and Arcade-based clients (see `/api/` and `/core/`)

## Core Module Structure
- `core/emulator.py`: PyBoy-based emulator wrapper for Pokémon Red, with modern logging (rich), SDL2/OpenGL backend support, debug options, and headless/interactive branching. The main API is `perform_emulator_action`, which takes a list of button presses and advances the emulator by a configurable number of frames (`wait_frames`).
- `core/actions.py`: Action types, mapping, and discrete action list for Gym environments
- `core/env_pokemon_red.py`: Gymnasium-compatible environment for Pokémon Red. The environment maps `ActionType.KEY_PRESS` and `ActionType.WAIT` to the emulator interface, and allows customizing timing through the `wait_frames` parameter.
- The `info` dictionary returned by `step()` and `reset()` contains extracted game state, including: player coordinates (x, y), current map ID, party count, player money, player name, rival name, badges (as a bitmask), pokedex_seen, time_played, party_species, and party_data.
  *   `player_x`: Player's x-coordinate (`int`)
  *   `player_y`: Player's y-coordinate (`int`)
  *   `map_id`: Current map ID (`int`)
  *   `party_count`: Number of Pokémon in the party (`int`)
  *   `player_money`: Player's money (`int`)
  *   `player_name`: Player's name (`str`)
  *   `rival_name`: Rival's name (`str`)
  *   `badges`: Bitmask of obtained badges (`int`)
  *   `pokedex_seen`: Number of Pokémon seen in the Pokédex (`int`)
  *   `time_played`: Tuple of (hours, minutes, seconds, frames) (`tuple[int, int, int, int]`)
  *   `party_species`: List of species IDs for Pokémon in the party (`list[int]`)
  *   `party_data`: Detailed data for each Pokémon in the party (`list[dict]`). Each dict contains:
    *   `species_id`: Species ID (`int`)
    *   `current_hp`: Current Hit Points (`int`)
    *   `status`: Status condition ID (`int`)
    *   `type1`: Type 1 ID (`int`)
    *   `type2`: Type 2 ID (`int`)
    *   `level`: Actual level (`int`)
    *   `moves`: List of move IDs (`list[int]`)
    *   `pp`: List of current PP for each move (`list[int]`)
    *   `trainer_id`: Original Trainer ID (`int`)
    *   `exp`: Experience points (`int`)
    *   `evs`: Dictionary of Effort Values (HP, Attack, Defense, Speed, Special) (`dict[str, int]`)
    *   `ivs`: Dictionary of Individual Values (HP, Attack, Defense, Speed, Special) (`dict[str, int]`)
    *   `stats`: Dictionary of current stats (Max HP, Attack, Defense, Speed, Special) (`dict[str, int]`)

## Legal
You must supply your own Pokémon Red ROM. This project does not distribute copyrighted ROMs.
