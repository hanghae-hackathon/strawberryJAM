from fastapi import Depends

from src.database import get_db
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.discussion import Discussion


class DiscussionRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_discussion(self, discussion_id: bytes):
        query = select(Discussion).where(Discussion.id == discussion_id)
        result = await self.session.execute(query)
        discussion = result.scalars().first()
        return discussion

    async def get_discussions(self, ids: list[bytes] | None):
        query = select(Discussion)

        if ids:
            query = query.where(Discussion.id.in_(ids))

        return (await self.session.scalars(query)).all()

    async def create_discussion(self, discussion: Discussion):
        self.session.add(instance=discussion)
        await self.session.commit()
        await self.session.refresh(instance=discussion)

        return discussion
