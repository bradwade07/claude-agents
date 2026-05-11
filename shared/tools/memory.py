"""Shared memory tool — two-tier (shared + private) SQLite backend."""
import os
import sqlite3
from pathlib import Path
from claude_agent_sdk import tool, create_sdk_mcp_server

SHARED_DB_PATH = os.getenv("SHARED_DB_PATH", "/app/shared/memory/shared.db")
SHARED_DB = Path(SHARED_DB_PATH)


def _init_db(path: Path):
    """Initialize memory table in a SQLite database."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _upsert(db: Path, key: str, value: str, category: str):
    """Insert or replace a memory entry."""
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT OR REPLACE INTO memories (key, value, category) VALUES (?,?,?)",
        (key, value, category)
    )
    conn.commit()
    conn.close()


def _search(db: Path, query: str):
    """Search memories by key, value, or category."""
    conn = sqlite3.connect(db)
    q = f"%{query.lower()}%"
    rows = conn.execute(
        "SELECT key, value, category FROM memories WHERE LOWER(key) LIKE ? OR LOWER(value) LIKE ? OR LOWER(category) LIKE ? ORDER BY updated_at DESC",
        (q, q, q)
    ).fetchall()
    conn.close()
    return rows


def build_memory_server(private_db: Path) -> object:
    """Factory: build MCP server with shared + private memory tools.

    Args:
        private_db: Path to this agent's private SQLite database.

    Returns:
        MCP server with tools: remember, remember_shared, recall.
    """
    _init_db(SHARED_DB)
    _init_db(private_db)

    @tool("remember", "Store private memory for this agent only", {"key": str, "value": str, "category": str})
    async def remember(args):
        """Store in private DB."""
        key = args["key"]
        value = args["value"]
        category = args.get("category", "general")
        _upsert(private_db, key, value, category)
        return {"content": [{"type": "text", "text": f"Private memory saved: {key} ({category})"}]}

    @tool("remember_shared", "Store shared memory all agents can access", {"key": str, "value": str, "category": str})
    async def remember_shared(args):
        """Store in shared DB."""
        key = args["key"]
        value = args["value"]
        category = args.get("category", "general")
        _upsert(SHARED_DB, key, value, category)
        return {"content": [{"type": "text", "text": f"Shared memory saved: {key} ({category})"}]}

    @tool("recall", "Search both shared and private memories", {"query": str})
    async def recall(args):
        """Search both databases, label results."""
        query = args["query"]
        shared = _search(SHARED_DB, query)
        private = _search(private_db, query)

        lines = []
        if shared:
            for key, value, category in shared:
                lines.append(f"[shared] {key} ({category}): {value}")
        if private:
            for key, value, category in private:
                lines.append(f"[private] {key} ({category}): {value}")

        text = "\n".join(lines) if lines else "No memories found."
        return {"content": [{"type": "text", "text": text}]}

    return create_sdk_mcp_server(
        name="memory",
        version="2.0.0",
        tools=[remember, remember_shared, recall]
    )
