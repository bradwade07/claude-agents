import sqlite3
import json
from pathlib import Path
from claude_agent_sdk import tool, create_sdk_mcp_server

DB_FILE = Path(__file__).parent.parent / "memory" / "memories.db"


def init_db():
    """Initialize memories table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@tool("remember", "Store a memory", {"key": str, "value": str, "category": str})
async def remember(args):
    """Store a memory entry."""
    key = args["key"]
    value = args["value"]
    category = args.get("category", "general")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO memories (key, value, category)
        VALUES (?, ?, ?)
    """, (key, value, category))
    conn.commit()
    conn.close()

    return {
        "content": [{"type": "text", "text": f"Remembered: {key} ({category})"}]
    }


@tool("recall", "Search memories by query", {"query": str})
async def recall(args):
    """Recall memories matching a query."""
    query = args["query"].lower()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT key, value, category FROM memories
        WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()

    if not results:
        return {"content": [{"type": "text", "text": "No memories found."}]}

    lines = [f"Memories matching '{query}':"]
    for key, value, category in results:
        lines.append(f"- {key} ({category}): {value}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


@tool("list_memories", "List all memories in a category", {"category": str})
async def list_memories(args):
    """List memories by category."""
    category = args["category"]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT key, value FROM memories
        WHERE category = ?
        ORDER BY updated_at DESC
    """, (category,))
    results = cursor.fetchall()
    conn.close()

    if not results:
        return {"content": [{"type": "text", "text": f"No memories in category '{category}'."}]}

    lines = [f"Memories in '{category}':"]
    for key, value in results:
        lines.append(f"- {key}: {value}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


init_db()
memory_server = create_sdk_mcp_server(
    name="memory",
    version="1.0.0",
    tools=[remember, recall, list_memories]
)
