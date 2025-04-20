"""
Action types and mapping for Pokémon Red environment.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from pyboy.utils import WindowEvent

class ActionType(str, Enum):
    KEY_PRESS = "tap"
    WAIT = "wait"

class KeyName(str, Enum):
    A = "A"
    B = "B"
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    START = "START"
    SELECT = "SELECT"

class Action(BaseModel):
    type: ActionType
    key: Optional[KeyName] = None  # Only set for KEY_PRESS

KEY_TO_EVENTS = {
    KeyName.A: (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
    KeyName.B: (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B),
    KeyName.UP: (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
    KeyName.DOWN: (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
    KeyName.LEFT: (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
    KeyName.RIGHT: (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
    KeyName.START: (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START),
    KeyName.SELECT: (WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_SELECT),
}

ALL_ACTIONS: List[Action] = [
    Action(type=ActionType.KEY_PRESS, key=k) for k in KeyName
] + [
    Action(type=ActionType.WAIT)
]
