"""
Action types and mapping for Pokémon Red environment.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

class ActionType(str, Enum):
    KEY_PRESS = "press"
    WAIT = "wait"

class KeyName(str, Enum):
    A = "a"
    B = "b"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    START = "start"
    SELECT = "select"

class Action(BaseModel):
    type: ActionType
    key: Optional[KeyName] = None  # Only set for KEY_PRESS

ALL_ACTIONS: List[Action] = [
    Action(type=ActionType.KEY_PRESS, key=k) for k in KeyName
] + [
    Action(type=ActionType.WAIT)
]
