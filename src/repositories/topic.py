from fastapi import Depends

from src.database import get_db
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func
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
    
    async def get_random_topic_ids(self, limit: int = 4):
        query = select(Topic.id).order_by(func.random()).limit(limit)
        result = await self.session.execute(query)
        topic_ids = [row[0] for row in result]
        return topic_ids
    
    async def get_topic_details_by_ids(self, topic_ids: list):
        query = select(Topic.id, Topic.title, Topic.image).where(Topic.id.in_(topic_ids))
        result = await self.session.execute(query)
        topics_details = result.fetchall()
        return topics_details
