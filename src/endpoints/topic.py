import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.models.topic import Topic
from src.repositories.topic import TopicRepository
from src.utils import get_templates


router = APIRouter(prefix="/topics", tags=["topic"])


class CreateTopicRequest(BaseModel):
    title: str
    description: str


class CreateTopicResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str


@router.get("/", response_class=HTMLResponse)
async def show_topic(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    topic_repo: TopicRepository = Depends(TopicRepository),
):

    random_topic_ids = await topic_repo.get_random_topic_ids()

    topics_details = await topic_repo.get_topic_details_by_ids(random_topic_ids)

    return templates.TemplateResponse(
        "topics.html", {"request": request, "topics_details": topics_details}
    )


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
