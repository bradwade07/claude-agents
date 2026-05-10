import json
import pathlib

SESSION_FILE = pathlib.Path(".bradbot_session.json")


def load_session_id() -> str | None:
    """Load persisted session ID from disk."""
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text()).get("session_id")
    return None


def save_session_id(session_id: str) -> None:
    """Save session ID to disk for resuming after restart."""
    SESSION_FILE.write_text(json.dumps({"session_id": session_id}))
