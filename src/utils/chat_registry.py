import sqlite3
import logging
import uuid
from pathlib import Path

from utils import constants
from utils.logging_config import setup_logger

setup_logger()
log = logging.getLogger(constants.APP_NAME)


def get_connection():
    """Create a connection to the application's SQLite database."""
    db_path = Path(__file__).parent.parent / "assistant_memory.sqlite"

    return sqlite3.connect(
        str(db_path),
        check_same_thread=False,
        isolation_level=None,
    )


def initialize_chat_registry():
    """Create the chat registry table if it doesn't exist."""

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_registry (
                thread_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    log.info("Chat registry initialized successfully")


def create_chat(title: str = "New Chat"):
    """Register a new conversation."""

    thread_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chat_registry (thread_id, title)
            VALUES (?, ?)
            """,
            (thread_id, title),
        )

    log.info("Created chat registry entry for thread_id=%s", thread_id)
    return thread_id


def get_all_chats():
    """Return registered conversations, newest activity first."""

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT thread_id, title, created_at, updated_at
            FROM chat_registry
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [
        {
            "chat_id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3],
        }
        for row in rows
    ]


def update_chat_title(thread_id: str, title: str):
    """Update a conversation's title."""

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE chat_registry
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE thread_id = ?
            """,
            (title, thread_id),
        )

    log.debug("Updated chat title for thread_id=%s", thread_id)


def update_chat(thread_id: str, user_input: str):
    """Update the last-activity timestamp for a conversation."""

    title = " ".join(user_input.split())[:40]
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE chat_registry
            SET title = CASE
                WHEN title = 'New Chat' then ?
                ELSE title
                END,
            updated_at = CURRENT_TIMESTAMP
            WHERE thread_id = ?
            """,
            (title or "New Chat", thread_id,),
        )