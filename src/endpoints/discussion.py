import uuid
from fastapi import APIRouter, Depends, Request, HTTPException
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
    try:
        discussion_bytes = discussion_id.bytes
        discussion = await repo.get_discussion(discussion_bytes)
        print(discussion_id)
        print(discussion)
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")

        return templates.TemplateResponse(
            request=request,
            name="discussion.html",
            context={"discussion_id": discussion_id, "discussion": discussion},
        )
    except Exception as e:
        print(f"Error reading discussion {discussion_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



class CreateDiscussionRequest(BaseModel):
    topic_id: uuid.UUID


class CreateDiscussionResponse(BaseModel):
    id: uuid.UUID


@router.post("/")
async def create_discussion(
    q: CreateDiscussionRequest,
    repo: DiscussionRepository = Depends(DiscussionRepository),
) -> CreateDiscussionResponse:
    try:
        print(q)
        discussion = await repo.create_discussion(
            discussion=Discussion.create(
                q.topic_id.bytes,
            )
        )

        return CreateDiscussionResponse(
            id=discussion.id
        )
    except Exception as e:
        print(f"Error creating discussion: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
