import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.user_activity_history_request import (
    UserActivityHistoryRequest,
    UserActivityHistoryResponse,
    UserActivityHistoryItem
)
from app.service.user_activity_history_service import UserActivityHistoryService
from app.db.user_activity_history_repository import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/history",
    tags=["user-activity-history"],
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)

# Dependency injection for service
def get_history_service() -> UserActivityHistoryService:
    """Dependency for history service."""
    return UserActivityHistoryService()


@router.get(
    "/{user_id}",
    response_model=UserActivityHistoryResponse,
    summary="Get user activity history",
    description="Retrieve the activity history for a specific user"
)
async def get_user_activity_history(
    user_id: str,
    service: UserActivityHistoryService = get_history_service()
) -> UserActivityHistoryResponse:
    """Get activity history for a specific user."""
    try:
        activities = service.get_user_activity_history(user_id)
        return UserActivityHistoryResponse(
            activities=[
                UserActivityHistoryItem(
                    history_id=activity.history_id,
                    summary_description=activity.summary_description,
                    date=activity.date,
                    user_id=activity.user_id
                ) for activity in activities
            ]
        )
    except ValueError as e:
        logger.warning(f"Invalid request for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity history"
        )
    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )