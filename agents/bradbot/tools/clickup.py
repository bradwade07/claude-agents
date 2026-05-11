import os
import httpx
from claude_agent_sdk import tool, create_sdk_mcp_server

CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
INBOX_LIST_ID = "901415799153"
BASE_URL = "https://api.clickup.com/api/v2"


def _get_headers():
    return {"Authorization": CLICKUP_API_KEY, "Content-Type": "application/json"}


@tool("add_task", "Add a task to ClickUp inbox", {"name": str, "description": str})
async def add_task(args):
    """Add a task to the ClickUp inbox list."""
    name = args["name"]
    description = args.get("description", "")

    payload = {
        "name": name,
        "description": description,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/list/{INBOX_LIST_ID}/task",
            json=payload,
            headers=_get_headers()
        )

    if response.status_code in (200, 201):
        task_data = response.json()
        task_id = task_data.get("task", {}).get("id", "unknown")
        return {"content": [{"type": "text", "text": f"Task created: {name} (ID: {task_id})"}]}
    else:
        return {
            "content": [{"type": "text", "text": f"Error creating task: {response.text}"}],
            "isError": True
        }


@tool("list_tasks", "List open tasks in ClickUp inbox", {})
async def list_tasks(args):
    """List all open tasks in the inbox."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/list/{INBOX_LIST_ID}/task?statuses=open",
            headers=_get_headers()
        )

    if response.status_code == 200:
        tasks = response.json().get("tasks", [])
        if not tasks:
            return {"content": [{"type": "text", "text": "No open tasks."}]}

        lines = ["Open tasks:"]
        for task in tasks:
            lines.append(f"- {task['name']} (ID: {task['id']})")

        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    else:
        return {
            "content": [{"type": "text", "text": f"Error fetching tasks: {response.text}"}],
            "isError": True
        }


@tool("complete_task", "Mark a task as done in ClickUp", {"task_id": str})
async def complete_task(args):
    """Mark a task as complete."""
    task_id = args["task_id"]

    payload = {"status": "done"}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/task/{task_id}",
            json=payload,
            headers=_get_headers()
        )

    if response.status_code == 200:
        return {"content": [{"type": "text", "text": f"Task {task_id} marked as done."}]}
    else:
        return {
            "content": [{"type": "text", "text": f"Error completing task: {response.text}"}],
            "isError": True
        }


clickup_server = create_sdk_mcp_server(
    name="clickup",
    version="1.0.0",
    tools=[add_task, list_tasks, complete_task]
)
