# Bradbot Scheduled Tasks

## Morning Briefing

**Schedule:** Daily at 8:00 AM (user timezone, UTC fallback)

**Trigger:** APScheduler job in `bot.py`

**Action:** Call `morning_briefing()` function

**Output:**
- Summarize today's calendar events (title, time, attendees)
- List overdue tasks from ClickUp inbox
- Highlight high-priority tasks due today
- Mention any urgent private notes (starred in memory)
- Suggest one action based on day's context
- Send via DM to user

**Format:**
```
Good morning! Here's your day:

**Calendar:**
- 10am: Sprint planning (with eng team)
- 2pm: 1:1 with X

**Tasks due today:**
- Finish Q2 planning (high priority)
- Review PR #123

**Notes:**
- Remember: hate meetings before 10am ✓ (no 9am conflicts today)

**Suggestion:** Start day with Q2 planning, you have 2hrs before standup.
```

**Quiet mode:** If no events, no overdue tasks, no urgent notes:
```
Good morning! Quiet day ahead. Clear to focus.
```

## Session Cleanup (Optional Future)

**Schedule:** Daily at 11:59 PM

**Action:** Archive old sessions (> 30 days) to backup, keep current session live

**Status:** Not yet implemented. Add if session DB grows large.

## Shared Memory Sync (Optional Future)

**Schedule:** Weekly on Sunday at 6 PM

**Action:** Summarize past week's learnings and save to shared memory

**Example:**
- "User prefers async feedback, dislikes sync meetings"
- "Urgent tasks often slip; set reminders 1 day before"

**Status:** Not yet implemented. Add if multi-agent coordination needed.
