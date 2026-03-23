from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.session import router as session_router
from app.api.prompt import router as prompt_router
from app.api.learning_sse import router as learning_sse_router
from app.api.user_activity_history import router as history_router


app = FastAPI()
app.include_router(session_router)
app.include_router(chat_router)

app.include_router(prompt_router)

app.include_router(learning_sse_router)
app.include_router(history_router)
