from typing import List

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    message: str
    # timestamp: str


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]


class ChatHistoryRequest(BaseModel):
    user_id: str
    session_id: str
