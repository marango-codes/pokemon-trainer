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
- `core/emulator.py`: PyBoy-based emulator wrapper for Pokémon Red
- `core/actions.py`: Action types, mapping, and discrete action list for Gym environments
- `core/env_pokemon_red.py`: Gymnasium-compatible environment for Pokémon Red

## Legal
You must supply your own Pokémon Red ROM. This project does not distribute copyrighted ROMs.

