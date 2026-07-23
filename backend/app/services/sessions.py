"""In-memory session store.

Carts live in process memory and are lost on restart. That is a deliberate
limit for now, not an oversight: nothing here is worth a database table until
sessions need to outlive a demo, and the shape below is what a persisted
version would store anyway.
"""

from app.graph.state import AgentState

_sessions: dict[str, AgentState] = {}


def get(session_id: str) -> AgentState:
    """The session's state, created empty on first use."""
    if session_id not in _sessions:
        _sessions[session_id] = AgentState(user_query="")
    return _sessions[session_id]


def clear() -> None:
    """Drop every session. Used by tests."""
    _sessions.clear()
