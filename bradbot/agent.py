import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage
from .sessions import load_session_id, save_session_id
from .tools.memory import memory_server
from .tools.clickup import clickup_server
from .tools.calendar import calendar_server

SYSTEM_PROMPT = """You are Bradbot, Brad's personal assistant on Discord.
You have access to his ClickUp tasks, Google Calendar, and personal memory store.
Use tools proactively to help with his requests. Be direct and concise — no filler, no pleasantries."""

ALLOWED_TOOLS = [
    "mcp__memory__remember",
    "mcp__memory__recall",
    "mcp__memory__list_memories",
    "mcp__clickup__add_task",
    "mcp__clickup__list_tasks",
    "mcp__clickup__complete_task",
    "mcp__calendar__list_events",
    "mcp__calendar__add_event",
]


async def bradbot_chat(user_message: str) -> str:
    """Process a message and return Bradbot's response."""
    session_id = load_session_id()

    options = ClaudeAgentOptions(
        model="claude-opus-4-7",
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "memory": memory_server,
            "clickup": clickup_server,
            "calendar": calendar_server,
        },
        allowed_tools=ALLOWED_TOOLS,
        permission_mode="acceptEdits",
        resume=session_id,
    )

    response_text = ""
    async for msg in query(prompt=user_message, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if hasattr(block, "text"):
                    response_text = block.text
        elif isinstance(msg, ResultMessage):
            save_session_id(msg.session_id)

    return response_text
