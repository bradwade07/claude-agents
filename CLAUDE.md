# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Bradbot

Personal Discord AI assistant using the Claude Agent SDK. Bradbot handles:
- Note-taking and memory (SQLite)
- ClickUp task management (inbox `901415799153`)
- Google Calendar integration
- Daily morning briefings (8am via APScheduler)
- Multi-turn conversation with persistent session memory (JSONL)

## Architecture

**Key Components:**
- `bradbot/agent.py` — Claude Agent SDK query wrapper, session management
- `bradbot/bot.py` — Discord bot entry point, APScheduler for morning briefing
- `bradbot/tools/` — MCP tool servers (memory, clickup, calendar)
  - `memory.py` — SQLite-backed notes, grocery list, general recall
  - `clickup.py` — ClickUp REST API wrapper (add_task, list_tasks, complete_task)
  - `calendar.py` — Google Calendar API (list_events, add_event)
- `bradbot/sessions.py` — Persist session_id to `.bradbot_session.json` between restarts

**Data Flow:**
1. User DM in Discord → `on_message` handler
2. Routes to `bradbot_chat(message)` in `agent.py`
3. `query()` with `resume=session_id` continues conversation thread
4. Claude Agent SDK loop calls MCP tools autonomously
5. Tools execute, results returned to Claude
6. Claude responds → DM back to user

**Session Persistence:**
- Each session ID is saved to `.bradbot_session.json`
- On restart, `load_session_id()` resumes the same conversation
- Full JSONL history stored by SDK at `~/.claude/projects/<cwd>/<session_id>.jsonl`

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Setup
cp .env.example .env  # Fill in secrets: DISCORD_TOKEN, ANTHROPIC_API_KEY, etc.

# Run bot
python -m bradbot

# Google Calendar setup (one-time)
# Download credentials.json from Google Cloud Console
# On first run, browser will open for OAuth2 approval
```

## Environment Variables

- `ANTHROPIC_API_KEY` — Claude API key
- `DISCORD_TOKEN` — Bot token from Discord Developer Portal
- `DISCORD_USER_ID` — Your numeric Discord user ID
- `CLICKUP_API_KEY` — ClickUp API token
- `GOOGLE_CALENDAR_CREDENTIALS` — Path to Google OAuth2 credentials.json (default: `credentials.json`)

## Testing

Manual:
1. DM bot: "remember grocery: milk, eggs"
2. DM: "what's on my grocery list?"
3. DM: "add ClickUp task: plan the week"
4. Kill and restart bot, DM: "what did I say earlier?" (session should resume)
5. Manually trigger morning briefing by running `bradbot.bot.morning_briefing()`

## Code Style

- No comments unless WHY is non-obvious
- Use async/await consistently
- Tools return `{"content": [...], "isError": bool}` format for Agent SDK
- Type hints optional but encouraged
- MCP tool naming: `mcp__{server}__{tool}` (automatic via `@tool` decorator)
