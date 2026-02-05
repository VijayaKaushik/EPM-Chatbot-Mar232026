
from google.adk.sessions import Session,DatabaseSessionService
import  uuid
from datetime import datetime
from typing import List

from app.models.init_session import InitSessionRequest, InitSessionResponse
db_url='sqlite:///./my_agent_data.db'

session_service = DatabaseSessionService(db_url=db_url)

async def create_session(request: InitSessionRequest)->InitSessionResponse:
   session_obj:Session = await session_service.create_session(
        app_name= "GoogleADK",
        user_id=request.user_id,
        session_id=str(uuid.uuid4()),
        state={
            "client_id": request.client_id,
            "user_id": request.user_id
        }
    )
   return InitSessionResponse(session_id=session_obj.id,created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

async def get_session_info(session_id:str,user_id:str):
    session_obj=await session_service.get_session(session_id=session_id,app_name= "GoogleADK",user_id=user_id)
    return session_obj.events


async def get_events(session_id:str,user_id:str):
    session_obj=await session_service.get_session(session_id=session_id,app_name= "GoogleADK",user_id=user_id)
    return session_obj.events

async def get_ai_user_chat_history(session_id:str,user_id:str) -> List[str]:
    events_data=await get_events(session_id=session_id,user_id=user_id)
    history=[]
    for event in events_data:
        if event.author =="user" :
            history.append(("user",event.content.parts[0].text))
        elif event.is_final_response() and event.content and event.content.parts:
            history.append(("ai",event.content.parts[0].text))

    return history


