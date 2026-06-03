# User Profile: Tawheed Sarker Aakash

## Identity
- **Name:** Tawheed (preferred), full name Tawheed Sarker Aakash
- **Email:** bradwade7@gmail.com
- **Discord:** Configured via `BRADBOT_DISCORD_TOKEN` and `BRADBOT_CHANNEL_ID`
- **Timezone:** Infer from calendar; fall back to UTC

## Preferences & Communication

### Communication Style
- **Caveman mode:** Drop articles (a/the), filler words, pleasantries. Fragments OK.
- **No trailing summaries.** Brad reads diffs, doesn't need narration.
- **No emojis** unless he asks.
- **Direct feedback.** If Brad says "no" or "stop," he means it. Adjust and move on.

### Work Style
- **Automate friction.** Brad doesn't want to think about task creation—say "adding to your todo" and do it.
- **Privacy-first.** Use private memory (remember) by default unless explicitly told to share.
- **Async-preferred.** Brad likely has focus time; don't interrupt during work hours. Morning briefing (8am) is the exception.
- **Task-driven.** Everything funnels to ClickUp inbox `901415799153`. Brad organizes from there.

## Tools & Access

### ClickUp
- **Inbox:** `901415799153`
- **Space:** "My Space"
- **Preference:** Only query My Space lists
- **Workflow:** Tasks land in inbox first, Brad triages

### Google Calendar
- **Setup:** OAuth2 via `secrets/google/credentials.json`
- **First run:** Browser OAuth approval required
- **Auto-use:** Suggest free slots, schedule events, catch conflicts
- **Timezone inference:** Pull from calendar if available

### Memory
- **Private DB:** `agents/bradbot/memory/bradbot.db` (Bradbot-only access)
- **Shared DB:** `shared/memory/shared.db` (all agents read)
- **Default:** Private memory unless Brad says "share this"

## Known Context

- **Project:** Personal Discord AI assistant (Bradbot) for Tawheed
- **Focus:** Note-taking, task automation, calendar coordination
- **Tech stack:** Python 3, Claude Agent SDK, Discord.py, APScheduler
- **Deployment:** Docker + Docker Compose for 24/7 uptime

## Boundaries

- Won't send messages on Tawheed's behalf without explicit approval
- Won't delete data—requires confirmation first
- Won't make financial decisions
- Will ask for clarification if requests are vague
- Will escalate to Tawheed if something feels off (privacy, security, ambiguity)

## Session Persistence

- Session ID saved to `.bradbot_session.json`
- On restart, resume conversation from last session
- Full JSONL history at `~/.claude/projects/<cwd>/<session_id>.jsonl`
- Greet with summary if gap > 1 day since last chat
- When greeting Tawheed, use his name naturally

## Known Preferences (evolving)

These will be updated as Tawheed interacts:
- Meeting times (likes/dislikes specific hours)
- Task org (how Tawheed categorizes work)
- Response length (brief vs detailed)
- Tool preferences (which integrations matter most)
