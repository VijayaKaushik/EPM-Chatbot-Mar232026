from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    user_msg: str


class ChatResponse(BaseModel):
    msg_id: str
    message: str
    created_at: str
