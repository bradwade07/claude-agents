"""Bradbot memory — uses shared memory tools with private DB."""
import os
import sys
from pathlib import Path

sys.path.insert(0, "/app")
from shared.tools.memory import build_memory_server

PRIVATE_DB_PATH = os.getenv("BRADBOT_PRIVATE_DB", "/app/bradbot/memory/bradbot.db")
PRIVATE_DB = Path(PRIVATE_DB_PATH)
memory_server = build_memory_server(PRIVATE_DB)
