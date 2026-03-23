from uuid import UUID

from click import UUID
from pydantic_core.core_schema import none_schema

from app.db.models.prompt import Prompt
from typing import List

from app.models.prompt_request import PromptResponse


class PromptRepository:  ## Data layer for interacting with DB for Prompt table
    def __init__(self):
        self.prompt_list = []

    def create(self, prompt: Prompt) -> Prompt:
        self.prompt_list.append(prompt)
        return prompt

    def update(self, prompt: Prompt) -> Prompt | None:
        for index, existing_prompt in enumerate(self.prompt_list):
            if existing_prompt.id == prompt.id:
                self.prompt_list[index] = prompt
                return prompt
        return None

    def get_all(self) -> List[Prompt]:
        return self.prompt_list

    def get_by_id(self, prompt_id: UUID) -> Prompt | None:
        for prompt in self.prompt_list:
            print(prompt.id, prompt_id)
            if prompt.id == prompt_id:
                return prompt
        return None

    def delete(self, prompt_id: UUID):
        prompt = self.get_by_id(prompt_id)
        if prompt:
            self.prompt_list.remove(prompt)
