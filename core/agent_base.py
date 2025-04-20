"""
Base Agent interface for all agent types.
"""
from abc import ABC, abstractmethod
from typing import Any

class Agent(ABC):
    """
    Abstract base class for all agent types (RL, LLM, Human).
    """
    @abstractmethod
    def choose_action(self, observation: Any) -> Any:
        """
        Given an observation, return an action.

        Args:
            observation (Any): The current game observation.

        Returns:
            Any: The chosen action.
        """
        pass
