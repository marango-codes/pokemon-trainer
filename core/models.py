"""
Pydantic models for actions, observations, and session metadata.
"""
from pydantic import BaseModel
from typing import Any, List, Optional

class Action(BaseModel):
    button: str
    pressed: bool

class Observation(BaseModel):
    frame: bytes  # Could be image bytes or encoded string
    info: Optional[dict] = None

class SessionMeta(BaseModel):
    session_id: str
    agent_type: str
    start_time: Optional[str]
    end_time: Optional[str]
    replay_available: bool = False
