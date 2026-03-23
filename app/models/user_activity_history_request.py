from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator


class UserActivityHistoryItem(BaseModel):
    """Response model for a single activity history entry."""
    history_id: str = Field(..., description="Unique identifier for the activity")
    summary_description: str = Field(..., description="Brief description of the activity")
    date: datetime = Field(..., description="When the activity occurred")
    user_id: str = Field(..., description="ID of the user who performed the activity")


class UserActivityHistoryResponse(BaseModel):
    """Response model for activity history list."""
    activities: List[UserActivityHistoryItem] = Field(
        default_factory=list,
        description="List of user activities"
    )


class UserActivityHistoryRequest(BaseModel):
    """Request model for activity history queries."""
    user_id: str = Field(..., min_length=1, description="ID of the user to get history for")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate that user_id is not empty or whitespace."""
        if not v.strip():
            raise ValueError("User ID cannot be empty or whitespace")
        return v.strip()