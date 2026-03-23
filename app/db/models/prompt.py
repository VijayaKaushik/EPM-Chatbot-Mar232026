from datetime import datetime

from uuid import UUID


## This is the entity class
class Prompt:
    __tablename__ = "prompt"
    id: UUID
    prompt_domain: str
    prompt_purpose: str
    prompt_text: str
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
