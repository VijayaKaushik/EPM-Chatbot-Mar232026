from pydantic import BaseModel


class InitSessionRequest(BaseModel):
    client_id: str
    user_id: str


class InitSessionResponse(BaseModel):
    session_id: str
    created_at: str
