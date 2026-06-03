import asyncio
import sqlite3
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage
from .sessions import load_session_id, save_session_id
from .tools.memory import memory_server
from .tools.clickup import clickup_server
from .tools.calendar import calendar_server

PRIVATE_DB = Path("/app/bradbot/memory/bradbot.db")
BRADBOT_DIR = Path(__file__).parent

_SYSTEM_PROMPT = None
_FILE_OBSERVER = None


class _PromptFileWatcher(FileSystemEventHandler):
    """Watch SOUL.md and USER.md for changes, clear cache on update."""

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.name in ("SOUL.md", "USER.md"):
            global _SYSTEM_PROMPT
            _SYSTEM_PROMPT = None
            print(f"[Bradbot] Reloading system prompt ({path.name} changed)")


def _start_file_watcher():
    """Start watching for file changes."""
    global _FILE_OBSERVER
    if _FILE_OBSERVER is not None:
        return

    _FILE_OBSERVER = Observer()
    _FILE_OBSERVER.schedule(_PromptFileWatcher(), str(BRADBOT_DIR), recursive=False)
    _FILE_OBSERVER.start()
    print("[Bradbot] File watcher started")


def _load_system_prompt() -> str:
    """Load SOUL.md + USER.md once at startup."""
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is not None:
        return _SYSTEM_PROMPT

    soul_path = BRADBOT_DIR / "SOUL.md"
    user_path = BRADBOT_DIR / "USER.md"

    parts = []
    if soul_path.exists():
        parts.append(soul_path.read_text())
    if user_path.exists():
        parts.append(user_path.read_text())

    _SYSTEM_PROMPT = "\n\n".join(parts) if parts else "You are Bradbot, Brad's personal Discord assistant."
    return _SYSTEM_PROMPT

ALLOWED_TOOLS = [
    "mcp__memory__remember",
    "mcp__memory__remember_shared",
    "mcp__memory__recall",
    "mcp__clickup__add_task",
    "mcp__clickup__list_tasks",
    "mcp__clickup__complete_task",
    "mcp__calendar__list_events",
    "mcp__calendar__add_event",
]


def _load_context() -> str:
    """Load relevant memory context from private DB."""
    try:
        conn = sqlite3.connect(PRIVATE_DB)
        rows = conn.execute(
            "SELECT key, value, category FROM memories ORDER BY updated_at DESC LIMIT 20"
        ).fetchall()
        conn.close()

        if not rows:
            return ""

        lines = ["## Your Recent Memories:"]
        for key, value, category in rows:
            lines.append(f"- {key} ({category}): {value}")
        return "\n".join(lines)
    except Exception:
        return ""


async def bradbot_chat(user_message: str) -> str:
    """Process a message and return Bradbot's response."""
    context = _load_context()
    system_prompt = _load_system_prompt()
    if context:
        system_prompt += f"\n\n{context}"

    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        system_prompt=system_prompt,
        mcp_servers={
            "memory": memory_server,
            "clickup": clickup_server,
            "calendar": calendar_server,
        },
        allowed_tools=ALLOWED_TOOLS,
        permission_mode="acceptEdits",
    )

    response_text = ""
    async for msg in query(prompt=user_message, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if hasattr(block, "text"):
                    response_text = block.text

    return response_text
