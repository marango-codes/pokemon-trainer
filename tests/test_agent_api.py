"""
Pytest unit tests for Agent API and SessionManager.
"""
import pytest
from core.agent_base import Agent
from core.session_manager import SessionManager

class DummyAgent(Agent):
    def choose_action(self, observation):
        return 'A'

def test_session_manager_expected():
    manager = SessionManager()
    agent = DummyAgent()
    manager.create_session('sess1', agent)
    obs = {'frame': b'123', 'info': {}}
    action = manager.step('sess1', obs)
    assert action == 'A'
    assert manager.get_history('sess1')[0] == (obs, 'A')

def test_switch_agent_edge():
    manager = SessionManager()
    agent1 = DummyAgent()
    agent2 = DummyAgent()
    manager.create_session('sess2', agent1)
    manager.switch_agent('sess2', agent2)
    obs = {'frame': b'456', 'info': {}}
    action = manager.step('sess2', obs)
    assert action == 'A'

def test_missing_session_failure():
    manager = SessionManager()
    with pytest.raises(KeyError):
        manager.step('nope', {})
