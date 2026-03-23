from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.models.chat_history import ChatHistoryRequest, ChatHistoryResponse
from app.models.chat_request import ChatRequest, ChatResponse
from app.service.chat_service import get_all_messages, exec_chat, exec_chat_sse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    return exec_chat(
        request
    )  ##exceptions are not handled at the moment ; add try catch later


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(request: ChatHistoryRequest):
    return await get_all_messages(request)


@router.post("/response", response_model=ChatResponse)
async def chat_response(request: ChatRequest):
    return await exec_chat(request)


@router.post("/sse")
async def chat_sse(request: ChatRequest):
    return StreamingResponse(
        exec_chat_sse(request), media_type="text/event-stream"
    )  ##exceptions are not handled at the moment ; add try catch later
