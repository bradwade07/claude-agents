import os
from datetime import datetime, timedelta
from pathlib import Path
from claude_agent_sdk import tool, create_sdk_mcp_server
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
import googleapiclient.discovery

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "credentials.json")
TOKEN_FILE = "token.json"

_service = None


def get_calendar_service():
    """Get authenticated Google Calendar service."""
    global _service
    if _service:
        return _service

    creds = None

    if Path(TOKEN_FILE).exists():
        creds = UserCredentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    _service = googleapiclient.discovery.build("calendar", "v3", credentials=creds)
    return _service


@tool("list_events", "List upcoming calendar events", {"days": int})
async def list_events(args):
    """List upcoming events from Google Calendar."""
    days = args.get("days", 7)

    service = get_calendar_service()
    now = datetime.utcnow()
    end = now + timedelta(days=days)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat() + "Z",
        timeMax=end.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return {"content": [{"type": "text", "text": "No events scheduled."}]}

    lines = [f"Events for next {days} days:"]
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "Unnamed event")
        lines.append(f"- {start}: {summary}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


@tool("add_event", "Create a calendar event", {"title": str, "date": str, "time": str})
async def add_event(args):
    """Create a new event in Google Calendar."""
    title = args["title"]
    date = args["date"]
    time = args.get("time", "09:00")

    try:
        start_dt = datetime.fromisoformat(f"{date}T{time}:00")
        end_dt = start_dt + timedelta(hours=1)
    except ValueError:
        return {
            "content": [{"type": "text", "text": "Invalid date/time format. Use YYYY-MM-DD and HH:MM."}],
            "isError": True
        }

    service = get_calendar_service()
    event = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Chicago"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Chicago"}
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return {"content": [{"type": "text", "text": f"Event created: {title} on {date} at {time}"}]}


calendar_server = create_sdk_mcp_server(
    name="calendar",
    version="1.0.0",
    tools=[list_events, add_event]
)
