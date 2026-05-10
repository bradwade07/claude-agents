# Bradbot — Personal Discord AI Assistant

A personal Discord bot powered by the Claude Agent SDK. Bradbot helps you manage daily life:

- **Notes & Memory** — Store and recall notes, grocery lists, and personal information
- **Task Management** — Sync with your ClickUp inbox (list `901415799153`)
- **Calendar** — Check and create events in Google Calendar
- **Daily Briefing** — Automatic morning summary at 8am (calendar + tasks + notes)
- **Persistent Sessions** — Bot remembers full conversation history across restarts

## Quick Start

### Prerequisites

- Python 3.9+
- Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Anthropic API key (from [console.anthropic.com](https://console.anthropic.com))
- ClickUp API token (from ClickUp workspace settings)
- Google OAuth2 credentials (from [Google Cloud Console](https://console.cloud.google.com))

### Setup

```bash
# Clone and install
git clone https://github.com/bradwade7/claude-agents.git
cd claude-agents
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your tokens and IDs

# Run
python -m bradbot
```

On first run, a browser window will open for Google Calendar OAuth2 approval. After approval, `token.json` is cached for future use.

## Architecture

Built on the Claude Agent SDK (`claude-agent-sdk` Python package) — the same engine powering Claude Code.

```
Discord channel msg → bradbot/bot.py (on_message, channel-scoped)
  ↓
bradbot/agent.py (claude_agent_sdk.query)
  ↓
MCP Tool Servers:
  • memory (SQLite notes)
  • clickup (REST API)
  • calendar (Google Calendar API)
  ↓
Claude Agent Loop (automatic tool execution)
  ↓
Response → Discord DM
```

Session IDs are persisted to `.bradbot_session.json`, so bot remembers conversations even after restarts.

## Commands (in configured Discord channel)

Examples:

- `remember grocery: milk, eggs, bread` — Store memory
- `what's on my grocery list?` — Search memories
- `add task: review Q1 planning` — Create ClickUp task
- `show my tasks` — List open ClickUp tasks
- `what's on my calendar next week?` — List calendar events
- `create event: Team sync on 2026-05-15 at 10:00` — Create calendar event

## Project Structure

```
bradbot/
├── __init__.py
├── __main__.py           # Entry point for `python -m bradbot`
├── bot.py               # Discord bot, APScheduler setup
├── agent.py             # Claude Agent SDK query wrapper
├── sessions.py          # Session persistence
└── tools/
    ├── __init__.py
    ├── memory.py        # SQLite-backed memory store
    ├── clickup.py       # ClickUp REST API tools
    └── calendar.py      # Google Calendar API tools
```

## Documentation

See [CLAUDE.md](CLAUDE.md) for development setup, testing, and architecture details.
