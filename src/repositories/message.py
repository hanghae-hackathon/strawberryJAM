from fastapi import Depends

from src.database import get_db
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_message(self, message_id: int):
        query = select(Message).where(Message.id == message_id)

        return (await self.session.scalars(query)).first()

    async def get_messages_by_discussion_id(self, discussion_id: int):
        query = (
            select(Message)
            .where(Message.discussion_id == discussion_id)
            .order_by(Message.created_at)
        )

        return (await self.session.scalars(query)).all()

    async def create_message(self, message: Message):
        self.session.add(instance=message)
        await self.session.commit()
        await self.session.refresh(instance=message)

        return message
