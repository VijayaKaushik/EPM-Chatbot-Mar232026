import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException

from app.db.models.prompt import Prompt
from app.db.prompt_repository import PromptRepository
from app.models.prompt_request import (
    PromptResponse,
    PromptRequest,
    PromptDTO,
    PromptDetailsDTO,
)


## Api   > service layer  > repository layer


class PromptService:
    def __init__(self):  ## this is the constructor of the class
        self.prompt_repository = (
            PromptRepository()
        )  # this we are doing dependency injection

    def create_prompt(self, request: PromptRequest) -> PromptResponse:
        prompt = Prompt()
        prompt.id = uuid.uuid4()
        prompt.prompt_domain = request.prompt_domain
        prompt.prompt_purpose = request.prompt_purpose
        prompt.prompt_text = request.prompt_text
        prompt.created_at = datetime.now()

        prompt = self.prompt_repository.create(
            prompt
        )  ## this will return the prompt to persist in db

        return PromptResponse(prompt_id=prompt.id, created_at=prompt.created_at)

    def get_all_prompts(self) -> PromptDetailsDTO:
        prompts = self.prompt_repository.get_all()
        prompt_dtos = []
        for prompt in prompts:  # convert entity to DTO
            prompt_dto = PromptDTO(
                prompt_id=prompt.id,
                prompt_domain=prompt.prompt_domain,
                prompt_purpose=prompt.prompt_purpose,
                prompt_text=prompt.prompt_text,
            )

            prompt_dtos.append(prompt_dto)

        return PromptDetailsDTO(
            prompts=prompt_dtos
        )  #  we should always convert entity to DTO(Data transfer object)

    def get_by_id(self, prompt_id):
        prompt = self.prompt_repository.get_by_id(prompt_id)
        prompt_dto = PromptDTO(
            prompt_id=prompt.id,
            prompt_domain=prompt.prompt_domain,
            prompt_purpose=prompt.prompt_purpose,
            prompt_text=prompt.prompt_text,
        )
        return prompt_dto

    def update_prompt(
        self, prompt_id: uuid.UUID, request: PromptRequest
    ) -> PromptResponse:
        prompt = self.prompt_repository.get_by_id(prompt_id)

        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Update fields
        prompt.prompt_domain = request.prompt_domain
        prompt.prompt_purpose = request.prompt_purpose
        prompt.prompt_text = request.prompt_text
        prompt.updated_at = datetime.now()

        updated_prompt = self.prompt_repository.update(prompt)

        return PromptResponse(
            prompt_id=updated_prompt.id, created_at=updated_prompt.created_at
        )

    def delete_prompt(self, prompt_id: uuid.UUID):
        self.prompt_repository.delete(prompt_id)
