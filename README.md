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
  /core/           # Game interface (PyBoy), session manager, pydantic models
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
2. **Place your Pokémon Red ROM** as `pokemon_red.gb` in the project root.
3. **Run tests:**
   ```sh
   pytest
   ```

## Usage
- RL agent: see `agents/rl_agent.py`
- LLM agent: see `agents/llm_agent.py` and API docs in `api/server.py`
- Human: see `agents/human_agent.py`
- Spectator: CLI and Arcade-based clients (see `/api/` and `/core/`)

## Legal
You must supply your own Pokémon Red ROM. This project does not distribute copyrighted ROMs.

---
See `PLANNING.md` for architecture and milestones.
