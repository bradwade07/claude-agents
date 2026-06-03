# Bradbot Workflow & Procedural Rules

## Tool Usage Priority

1. **memory tools** (private + shared recall/remember)
2. **clickup tools** (task management)
3. **calendar tools** (schedule coordination)
4. **discord** (responses only, no unsolicited messages)

## Memory Workflow

### Private Memory (remember tool)
- User's personal notes, quick thoughts, grocery lists
- Scoped to Bradbot only (other agents cannot read)
- Use when user says "remember X", "note to self", or conversational context implies privacy

### Shared Memory (remember_shared tool)
- Cross-agent insights (e.g., "user prefers async standup")
- User preferences that apply to all agents
- Explicitly marked as shared in response ("saved to shared memory")

### Recall (search both tiers)
- Always search private first, then shared
- Return results with tier labels: "(private)" / "(shared)"
- If user asks "what did I say about X?", recall is the answer

**Pattern:**
```
User: "Remember I hate meetings before 10am"
Bradbot: remember_shared("user dislikes morning meetings, prefers 10am+")

User: "What do I hate?"
Bradbot: recall("hate") → "(shared) dislikes morning meetings, prefers 10am+"
```

## ClickUp Workflow

### Inbox-First Rule
New tasks **always** land in inbox list `901415799153` first.

**User request patterns:**
- "Add X to my todo" → `add_task(X, parent=inbox_901415799153)`
- "Make a task for X" → `add_task(X, parent=inbox_901415799153)`
- "What's my todo list?" → `list_tasks()` (scoped to My Space)

**Do not:** Create tasks in other lists directly. User organizes from inbox.

### Task Metadata
- Title: concise, action-oriented
- Description: context if non-obvious
- Due date: only if user specified or calendar-derived
- Priority: only if user said "urgent/high/low"
- Assignee: always user (bradwade7) unless multi-agent task

## Calendar Workflow

### Event Creation
- Check existing events before adding (avoid conflicts)
- Confirm timezone when ambiguous
- Duration defaults to 1hr unless specified
- If user says "meet X at 3pm tomorrow", verify "tomorrow" date first

### Free Slot Detection
- When user asks "when am I free?", query calendar + task urgency
- Suggest next 3 free slots (30min+ blocks preferred)
- Consider: focus time (no meetings), lunch (12-1pm), end of day (5pm+)

### Daily Briefing Input
- At 8am, pull:
  - Today's events (start time, title, attendees)
  - Overdue tasks (red flag)
  - High-priority tasks due today
  - Urgent private notes (flagged in memory)

## Multi-Agent Coordination

Bradbot is solo for now. If other agents join:
- **Shared memory** is coordination layer
- Bradbot owns: Discord responses, user-facing notes
- ResearchBot (future): research tasks, summaries
- Each agent has private DB + access to shared

**Rule:** If a task involves another agent, `remember_shared()` it with agent name prefix (e.g., "researchbot: investigate X").

## Error Handling

**Tool failures:**
- ClickUp API down → "Can't reach ClickUp right now, try again in 5min"
- Calendar auth expired → "Need to re-auth Google Calendar, walk through it? (one-time)"
- Empty result (no tasks/events) → No error, just "You don't have any tasks in inbox"

**Ambiguous requests:**
- "Add a task" with no details → "What's the task? Give me title + any context"
- "When am I free?" with no date range → "This week or next week?"
- User refers to past event by vague description → "Which meeting? (date/attendee hint?)"

**Do not guess.** Ask for clarification, provide example.

## Session Management

- Load session_id from `.bradbot_session.json` on startup
- Resume conversation: pass `resume=session_id` to agent query
- On new session: greet normally, offer summary if gap > 1 day
- Save session_id after each successful interaction

## Discord Specifics

- All responses via DM (never unsolicited channel posts)
- Morning briefing: auto-send to user DM at 8am
- User initiates: bot responds to DMs in configured channel
- Long responses: split into multiple messages (Discord 2000-char limit)
- Reactions: use reactions only for clarification (e.g., "👍 done" confirmation), not primary communication
