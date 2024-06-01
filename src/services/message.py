from fastapi import Depends
from src.models.message import Message
from src.repositories.message import MessageRepository


class MessageService:
    def __init__(self, repo: MessageRepository = Depends()):
        self.repo = repo

    async def create_message(self, message: Message):
        return await self.repo.create_message(message=message)

    async def update_message(self, message: Message):
        return await self.repo.update_message(message=message)

    async def get_message(self, message_id: int):
        return await self.repo.get_message(message_id=message_id)

    async def get_messages_by_discussion_id(self, discussion_id: int):
        return await self.repo.get_messages_by_discussion_id(
            discussion_id=discussion_id
        )
