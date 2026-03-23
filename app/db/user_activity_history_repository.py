import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Iterator
from app.models.user_activity_history import UserActivityHistory


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class UserActivityHistoryRepository:
    """Repository for managing user activity history in SQLite database."""

    def __init__(self, db_path: str | Path = "user_activity.db") -> None:
        """Initialize the repository with database path."""
        self.db_path = Path(db_path)
        self._create_table()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            conn.close()

    def _create_table(self) -> None:
        """Create the user_activity_history table if it doesn't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_activity_history (
                    history_id TEXT PRIMARY KEY,
                    summary_description TEXT NOT NULL,
                    date TEXT NOT NULL,
                    user_id TEXT NOT NULL
                )
            """)
            conn.commit()

    def create(self, history: UserActivityHistory) -> UserActivityHistory:
        """Create a new activity history entry."""
        with self._get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO user_activity_history
                    (history_id, summary_description, date, user_id)
                    VALUES (?, ?, ?, ?)
                """, (
                    history.history_id,
                    history.summary_description,
                    history.date.isoformat(),
                    history.user_id
                ))
                conn.commit()
                return history
            except sqlite3.IntegrityError as e:
                raise DatabaseError(f"Failed to create history entry: {e}") from e

    def get_all_by_user_id(self, user_id: str) -> List[UserActivityHistory]:
        """Get all activity history for a specific user."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT history_id, summary_description, date, user_id
                FROM user_activity_history
                WHERE user_id = ?
                ORDER BY date DESC
            """, (user_id,))
            rows = cursor.fetchall()

        return [
            UserActivityHistory(
                history_id=row[0],
                summary_description=row[1],
                date=datetime.fromisoformat(row[2]),
                user_id=row[3]
            ) for row in rows
        ]

    def get_by_id(self, history_id: str) -> Optional[UserActivityHistory]:
        """Get a specific activity history entry by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT history_id, summary_description, date, user_id
                FROM user_activity_history
                WHERE history_id = ?
            """, (history_id,))
            row = cursor.fetchone()

        if row:
            return UserActivityHistory(
                history_id=row[0],
                summary_description=row[1],
                date=datetime.fromisoformat(row[2]),
                user_id=row[3]
            )
        return None

    def get_all(self) -> List[UserActivityHistory]:
        """Get all activity history entries."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT history_id, summary_description, date, user_id
                FROM user_activity_history
                ORDER BY date DESC
            """)
            rows = cursor.fetchall()

        return [
            UserActivityHistory(
                history_id=row[0],
                summary_description=row[1],
                date=datetime.fromisoformat(row[2]),
                user_id=row[3]
            ) for row in rows
        ]