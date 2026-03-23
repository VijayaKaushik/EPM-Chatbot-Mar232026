from uuid import UUID

from fastapi import APIRouter

from app.models.prompt_request import (
    PromptResponse,
    PromptRequest,
    PromptDTO,
    PromptDetailsDTO,
)
from app.service.prompt_service import PromptService

router = APIRouter(prefix="/prompt", tags=["prompt"])
service = PromptService()


@router.post("", response_model=PromptResponse)
def prompt_create(request: PromptRequest):
    return service.create_prompt(request)


@router.get("", response_model=PromptDetailsDTO)
def get_all_prompt():
    return service.get_all_prompts()


@router.get("/{prompt_id}", response_model=PromptDTO)
def get_prompt_details(prompt_id: UUID):
    return service.get_by_id(prompt_id)


@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: UUID):
    service.delete_prompt(prompt_id)


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: UUID, request: PromptRequest):
    return service.update_prompt(prompt_id, request)
