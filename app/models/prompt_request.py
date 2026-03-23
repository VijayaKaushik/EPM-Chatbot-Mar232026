from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt_domain: str
    prompt_purpose: str
    prompt_text: str


class PromptResponse(BaseModel):
    prompt_id: UUID
    created_at: datetime


class PromptDTO(BaseModel):
    prompt_id: UUID
    prompt_purpose: str
    prompt_domain: str
    prompt_text: str


class PromptDetailsDTO(BaseModel):
    prompts: List[PromptDTO]
