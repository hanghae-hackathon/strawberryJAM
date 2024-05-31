from fastapi import Depends

from src.database import get_db
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.topic import Topic


class TopicRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_topic(self, topic_id: int):
        query = select(Topic).where(Topic.id == topic_id)

        return (await self.session.scalars(query)).first()

    async def create_topic(self, topic: Topic):
        self.session.add(instance=topic)
        await self.session.commit()
        await self.session.refresh(instance=topic)

        return topic
