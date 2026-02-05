
from google.adk.runners import Runner
from dotenv import load_dotenv
#from app.service.ai_workflow.session_service import session_service  ## this is used for im memory session saves
from app.service.ai_workflow.db_session_service import session_service
from app.agent.manager.agent   import manager_agent
from google.genai import types # converts in required object for runner to run

load_dotenv()

# runner  needs:session , agent, app name. runner executes user query , also gathers info from session  thru session service

runner = Runner(
    agent=manager_agent,
    session_service=session_service,
    app_name= "GoogleADK"

)

def run_query(query:str,session_id:str,user_id:str) -> str | None:
    new_msg=types.Content(
        role="user",
        parts=[
            types.Part(text=query)
        ]

    )
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=new_msg
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print (f"final response :{event.content.parts[0].text}")

                ##  persist in the db the ai /user chat
                return event.content.parts[0].text
    return None  # we will refactor it later



def run_query_sse(query:str,session_id:str,user_id:str) :
    new_msg=types.Content(
        role="user",
        parts=[
            types.Part(text=query)
        ]

    )
    print("calling runner:")
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=new_msg
    ):
     print("returning event:")
     yield event






