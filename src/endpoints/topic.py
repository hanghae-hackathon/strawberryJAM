import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.models.topic import Topic
from src.repositories.topic import TopicRepository


router = APIRouter(prefix="/topics", tags=["topic"])


class CreateTopicRequest(BaseModel):
    title: str
    description: str


class CreateTopicResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str


@router.post("/")
async def create_topic(
    q: CreateTopicRequest,
    repo: TopicRepository = Depends(TopicRepository),
) -> CreateTopicResponse:
    topic = await repo.create_topic(topic=Topic.create(**q.model_dump()))

    return CreateTopicResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description,
    )
