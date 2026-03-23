import asyncio

from fastapi import APIRouter
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/learning-sse", tags=["sse"])


@router.get("")
async def stream():
    async def even_generator():
        i = 0
        while True:
            yield f"data: {i}"
            i = i + 1
            await asyncio.sleep(1)

    return StreamingResponse(even_generator(), media_type="text/event-stream")
