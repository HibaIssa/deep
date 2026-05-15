import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from app.config import DB_PATH


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                selected_role TEXT NOT NULL,
                coverage_percent REAL NOT NULL,
                report_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_user(username: str, password_hash: str, salt: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
            (username, password_hash, salt, utc_now()),
        )
        return int(cursor.lastrowid)


def get_user_by_username(username: str):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(user_id: int):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def save_report(user_id: int, title: str, report: dict) -> int:
    gap_analysis = report["gap_analysis"]
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO saved_reports
            (user_id, title, selected_role, coverage_percent, report_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title,
                report["selected_role"],
                gap_analysis["coverage_percent"],
                json.dumps(report),
                utc_now(),
            ),
        )
        return int(cursor.lastrowid)


def list_reports(user_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, selected_role, coverage_percent, created_at
            FROM saved_reports
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_report(user_id: int, report_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT report_json FROM saved_reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        ).fetchone()
        return json.loads(row["report_json"]) if row else None


def delete_report(user_id: int, report_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM saved_reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        )
        return cursor.rowcount > 0
