import logging
from typing import List
from app.db.user_activity_history_repository import (
    UserActivityHistoryRepository,
    DatabaseError
)
from app.models.user_activity_history import UserActivityHistory

logger = logging.getLogger(__name__)


class UserActivityHistoryService:
    """Service layer for user activity history operations."""

    def __init__(self, repository: UserActivityHistoryRepository | None = None) -> None:
        """Initialize the service with a repository."""
        self.repository = repository or UserActivityHistoryRepository()

    def get_user_activity_history(self, user_id: str) -> List[UserActivityHistory]:
        """Get activity history for a specific user."""
        if not user_id.strip():
            raise ValueError("User ID cannot be empty")

        try:
            activities = self.repository.get_all_by_user_id(user_id)
            logger.info(f"Retrieved {len(activities)} activities for user {user_id}")
            return activities
        except DatabaseError as e:
            logger.error(f"Failed to get activity history for user {user_id}: {e}")
            raise

    def get_all_activity_history(self) -> List[UserActivityHistory]:
        """Get all activity history entries."""
        try:
            activities = self.repository.get_all()
            logger.info(f"Retrieved {len(activities)} total activities")
            return activities
        except DatabaseError as e:
            logger.error(f"Failed to get all activity history: {e}")
            raise

    def create_activity_history(self, history: UserActivityHistory) -> UserActivityHistory:
        """Create a new activity history entry."""
        try:
            created = self.repository.create(history)
            logger.info(f"Created activity history {created.history_id} for user {created.user_id}")
            return created
        except DatabaseError as e:
            logger.error(f"Failed to create activity history: {e}")
            raise