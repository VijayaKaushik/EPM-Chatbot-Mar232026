import json
from datetime import datetime

from app.models.chat_history import ChatHistoryRequest, ChatMessage, ChatHistoryResponse
from app.models.chat_request import ChatRequest, ChatResponse
from app.service.ai_workflow.runner_service import run_query, run_query_sse
#from app.service.ai_workflow.session_service import get_ai_user_chat_history  ## this is used for inmemory session saving
from app.service.ai_workflow.db_session_service  import get_ai_user_chat_history

import uuid


## prevalidation is missing (check for empty message, session id exists)
def exec_chat(request: ChatRequest) -> ChatResponse:
    ai_response= run_query(query=request.user_msg,session_id=request.session_id,user_id=request.user_id)
    return ChatResponse(msg_id=str(uuid.uuid4()), message=ai_response,created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

async def exec_chat_sse(request: ChatRequest):
    print("inside chat service sse")
    for ai_response in run_query_sse(
        query=request.user_msg,
        session_id=request.session_id,
        user_id=request.user_id
    ):
        print("returning agent response")
        response = ChatResponse(
            msg_id=str(uuid.uuid4()),
            message=ai_response,  # or ai_response.content if needed
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        # Format as SSE
        yield f"data: {json.dumps(response.model_dump())}\n\n"


async def get_all_messages(request: ChatHistoryRequest):
    ai_user_history= await get_ai_user_chat_history(session_id=request.session_id, user_id=request.user_id)
    chat_history = []
    for role,message in ai_user_history: ## converting list of tuple to list of ChatMessage object
        chat_history.append(ChatMessage(role=role,message=message))

    return ChatHistoryResponse(messages=chat_history)