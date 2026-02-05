from fastapi import APIRouter

from app.models.init_session import InitSessionRequest, InitSessionResponse
#from app.service.ai_workflow.session_service import get_session_info, create_session   # this will be used for in memory

from app.service.ai_workflow.db_session_service import get_session_info, create_session

router = APIRouter(prefix="/session",tags=["session"])

@router.post("/init", response_model=InitSessionResponse)
async def init_session(request: InitSessionRequest):
    return await create_session(request)

@router.get("/{session_id}/{user_id}")
async def get_session(session_id:str,user_id:str):
    return await get_session_info(session_id,user_id)
