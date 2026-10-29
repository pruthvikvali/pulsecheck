
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "pulsecheck.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_incident_table():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                status TEXT NOT NULL,
                http_status INTEGER,
                response_time_ms REAL,
                error_message TEXT,
                checked_at TEXT NOT NULL
            )
            """
        )


def save_incident(
    service_name,
    status,
    http_status,
    response_time_ms,
    error_message,
    checked_at,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO incidents (
                service_name,
                status,
                http_status,
                response_time_ms,
                error_message,
                checked_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                service_name,
                status,
                http_status,
                response_time_ms,
                error_message,
                checked_at,
            ),
        )


def get_recent_incidents(limit=20):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM incidents
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]
