from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class UserActivityHistory:
    """Represents a single user activity history entry."""
    summary_description: str
    date: datetime
    user_id: str
    history_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        """Validate the data after initialization."""
        if not self.summary_description.strip():
            raise ValueError("Summary description cannot be empty")
        if not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if self.date > datetime.now():
            raise ValueError("Activity date cannot be in the future")