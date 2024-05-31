import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.models.discussion import Discussion
from src.repositories.discussion import DiscussionRepository
from src.utils import get_templates


router = APIRouter(prefix="/discussions", tags=["discussion"])


@router.get("/{discussion_id}", response_class=HTMLResponse)
async def read_discussion(
    request: Request,
    discussion_id: uuid.UUID,
    templates: Jinja2Templates = Depends(get_templates),
    repo: DiscussionRepository = Depends(DiscussionRepository),
):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={"discussion_id": discussion_id},
    )


class CreateDiscussionRequest(BaseModel):
    title: str
    content: str
    topic_id: bytes


class CreateDiscussionResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str


@router.post("/")
async def create_discussion(
    q: CreateDiscussionRequest,
    repo: DiscussionRepository = Depends(DiscussionRepository),
) -> CreateDiscussionResponse:
    discussion = await repo.create_discussion(
        discussion=Discussion.create(**q.model_dump())
    )

    return CreateDiscussionResponse(
        id=discussion.id,
        title=discussion.title,
        content=discussion.content,
    )
