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
- `agents/bradbot/agent.py` — Claude Agent SDK query wrapper, session management
- `agents/bradbot/bot.py` — Discord bot entry point, APScheduler for morning briefing
- `agents/bradbot/tools/` — MCP tool servers (memory, clickup, calendar)
  - `memory.py` — thin wrapper, uses shared memory factory
- `agents/bradbot/memory/` — SQLite DB (private to Bradbot)
  - `bradbot.db` — private notes, cache, state (gitignored)
- `shared/tools/memory.py` — two-tier memory factory
  - `build_memory_server(private_db)` → MCP server with 3 tools
    - `remember` → write to private DB
    - `remember_shared` → write to shared DB (all agents can read)
    - `recall` → search both DBs, label results
- `shared/memory/` — SQLite DB (shared by all agents)
  - `shared.db` — user prefs, grocery list, cross-agent data (gitignored)
  - `clickup.py` — ClickUp REST API wrapper (add_task, list_tasks, complete_task)
  - `calendar.py` — Google Calendar API (list_events, add_event)
- `agents/bradbot/sessions.py` — Persist session_id to `.bradbot_session.json` between restarts

**Data Flow:**
1. Message in configured channel → `on_message` handler (filters by channel ID)
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
edit secrets/.env  # Fill in secrets: BRADBOT_DISCORD_TOKEN, ANTHROPIC_API_KEY, etc.

# Run bot
python -m bradbot

# Google Calendar setup (one-time)
# Download credentials.json from Google Cloud Console
# On first run, browser will open for OAuth2 approval
```

### Docker (24/7 recommended)
```bash
# Build base image + Bradbot (first time)
docker compose build

# Run
docker compose up -d

# View logs
docker compose logs -f bradbot

# Stop
docker compose down

# Rebuild after code changes
docker compose build --no-cache
docker compose up -d
```

**Architecture:** 
- Shared base image `claude-agents-base:latest` (Python 3.14 + all deps)
- One agent per container in `agents/` directory (Bradbot, ResearchBot, etc.)
- Volumes:
  - `shared/memory/` → `/app/shared/memory` (all agents R/W)
  - `agents/{agent}/memory/` → `/app/{agent}/memory` (agent R/W only)
  - `secrets/` → `/app/secrets` (read-only)

**Memory tiers:**
- **Private:** Agent writes to `agents/{agent}/memory/{agent}.db` — only that agent reads/writes
- **Shared:** Any agent can write to `shared/memory/shared.db` — all agents see it
- Tools: `remember` (private), `remember_shared` (shared), `recall` (both)

**Scaling:** Add new agents in `agents/` directory. Create `agents/newagent/Dockerfile` + service in `docker-compose.yml`. Copy 3-line `agents/newagent/tools/memory.py` wrapper pointing to `agents/newagent/memory/newagent.db`.

## Environment Variables

- `ANTHROPIC_API_KEY` — Claude API key
- `BRADBOT_DISCORD_TOKEN` — Bot token from Discord Developer Portal
- `BRADBOT_CHANNEL_ID` — Discord channel ID where bot listens + posts briefings
- `CLICKUP_API_KEY` — ClickUp API token
- `GOOGLE_CALENDAR_CREDENTIALS` — Path to Google OAuth2 credentials.json (default: `secrets/google/credentials.json`)

All secrets live in `secrets/` directory (gitignored). Subdir `secrets/google/` holds OAuth2 `credentials.json` and auto-generated `token.json`.

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
