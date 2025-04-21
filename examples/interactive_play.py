"""Interactive script to play Pokemon Red using the Gymnasium environment.

Allows manual stepping through the environment using keyboard inputs mapped
to game actions.

Usage:
    python interactive_play.py

Controls:
Enter the number corresponding to the desired action.
Enter 'q' to quit.
"""

import os
import sys

# --- Path Setup --- Must happen before core imports ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- End Path Setup ---

from core.env_pokemon_red import PokemonRedEnv  # noqa: E402
from core.actions import ALL_ACTIONS, ActionType  # noqa: E402

def run_interactive():
    """Runs the interactive Pokemon Red game session."""
    save_state_path = "interactive_state.sav"

    print("Initializing Pokemon Red environment for interactive play...")
    # Use the base environment directly with human rendering
    env = PokemonRedEnv(render_mode='human')

    print("Environment initialized. Resetting...")
    obs, info = env.reset()
    print("Reset complete. Starting interactive loop.")

    if os.path.exists(save_state_path):
        try:
            print(f"Loading state from {save_state_path}...")
            env.load_state(save_state_path)
            print("State loaded successfully.")
        except Exception as e:
            print(f"Error loading state: {e}. Starting new game.")
            if not env.start_new_game():
                print("Error: Failed to start new game automatically.")
                env.close()
                return # Exit if starting failed
    else:
        print("No save state found. Starting new game automatically...")
        if not env.start_new_game():
            print("Error: Failed to start new game automatically.")
            env.close()
            return # Exit if starting failed

    terminated = False
    truncated = False
    total_reward = 0

    # Initial render call might be needed to ensure window pops up immediately
    env.render()

    while not terminated and not truncated:
        # --- Ticking Compromise --- #
        print("\nGame progressing... (Ticking emulator 60 times)")
        for _ in range(60): # Simulate approx 1 second of game time
             env.render() # Tick emulator in human mode
        print("Ready for next action.")
        # ------------------------- #

        print("\n--- Available Actions ---")
        for i, action in enumerate(ALL_ACTIONS):
            if action.type == ActionType.KEY_PRESS:
                print(f"{i}: Press {action.key.name}")
            else:
                print(f"{i}: Wait")
        print("'q': Quit")

        action_input = input("Enter action number (or 'q' to quit): ").strip().lower()

        if action_input == 'q':
            print("Quitting interactive session.")
            try:
                print(f"Saving state to {save_state_path}...")
                env.save_state(save_state_path)
                print("State saved successfully.")
            except Exception as e:
                print(f"Error saving state: {e}")
            break

        try:
            action_index = int(action_input)
            if not 0 <= action_index < len(ALL_ACTIONS):
                raise ValueError("Action index out of range.")
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid number or 'q'.")
            continue

        print(f"Performing action: {ALL_ACTIONS[action_index]}")
        obs, reward, terminated, truncated, info = env.step(action_index)
        total_reward += reward

        # Render after step (for human mode, this ticks the emulator)
        env.render()

        print("\n--- Step Result ---")
        print(f"Observation Shape: {obs.shape if obs is not None else 'None'}")
        print(f"Reward: {reward}")
        print(f"Terminated: {terminated}")
        print(f"Truncated: {truncated}")
        print("Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print(f"Total Reward: {total_reward}")

        if terminated:
            print("\nEpisode terminated.")
        if truncated:
            print("\nEpisode truncated.")

    print("Closing environment.")
    env.close()

if __name__ == "__main__":
    run_interactive()
