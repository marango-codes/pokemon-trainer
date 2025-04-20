"""
Session manager for orchestrating agent play, switching, and replay.
"""
from typing import Optional, Dict, Any
from .agent_base import Agent

class SessionManager:
    """
    Manages game sessions, agent switching, and replay recording.
    """
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str, agent: Agent):
        self.sessions[session_id] = {
            'agent': agent,
            'history': [],
            'state': None
        }

    def step(self, session_id: str, observation: Any) -> Any:
        agent = self.sessions[session_id]['agent']
        action = agent.choose_action(observation)
        self.sessions[session_id]['history'].append((observation, action))
        return action

    def switch_agent(self, session_id: str, new_agent: Agent):
        self.sessions[session_id]['agent'] = new_agent

    def get_history(self, session_id: str):
        return self.sessions[session_id]['history']
