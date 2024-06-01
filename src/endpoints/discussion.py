from fastapi import HTTPException
import uuid
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.models.discussion import Discussion
from src.repositories.discussion import DiscussionRepository
from src.repositories.topic import TopicRepository
from src.services.gpt import GPTService
from src.utils import get_templates
from langchain.schema.messages import HumanMessage


router = APIRouter(prefix="/discussions", tags=["discussion"])


@router.get("/{discussion_id}", response_class=HTMLResponse)
async def read_discussion(
    request: Request,
    discussion_id: uuid.UUID,
    templates: Jinja2Templates = Depends(get_templates),
    discussion_repo: DiscussionRepository = Depends(DiscussionRepository),
    topic_repo: TopicRepository = Depends(TopicRepository),
    gpt_service: GPTService = Depends(GPTService),
):
    discussion = await discussion_repo.get_discussion(discussion_id=discussion_id.bytes)
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    topic = await topic_repo.get_topic(topic_id=discussion.topic_id)

    init_prompt = (
        f"안녕하세요\n "
        "지금부터 너는 성인을 위한 토론 능력, 디지털 문해력 향상을 위한 토의를 진행하는 전문가야.\n "
        "다음 뉴스기사를 토대로, 사용자가 뉴스 기사를 충분히 이해했는지, 찬반 토론을 진행할 수 있는지, 비판적으로 사고하는 능력을 가지고 있는지를 판단하려고 해.\n "
        "질문은 너무 세부사항을 물어보는 구체적인 질문은 아니면서, 충분히 기사를 이해하고 있는지, 비판적이고 논리적인 사고를 하고 있는지를 판단하는 적절한 질문이어야 해. \n"
        "질문에 대한 답변은 반드시 주어진 기사에서 찾아볼 수 있어야 해. Only follow my instruction.\n "
        "뉴스기사 전문: \n"
        "₩₩₩ \n"
        f"{ topic.description }"
        "₩₩₩ \n"
        "My instruction: \n"
        "먼저, 유저는 위 뉴스기사를 바탕으로 요약문을 작성해서 제공할거야. 이제, 'Ready to Debate'만 출력해. \n"
        "다른 말은 출력하지 마. \n"
    )
    stream = gpt_service.chat(messages=[HumanMessage(content=init_prompt)])

    init_message = ""

    for message in stream:
        init_message += message.content

    return templates.TemplateResponse(
        request=request,
        name="discussion.html",
        context={
            "discussion_id": discussion_id,
            "topic_description": topic.description,
            "topic_title": topic.title,
            "init_message": init_message,
        },
    )



class CreateDiscussionRequest(BaseModel):
    topic_id: uuid.UUID


class CreateDiscussionResponse(BaseModel):
    id: uuid.UUID


@router.post("/")
async def create_discussion(
    q: CreateDiscussionRequest,
    discussion_repo: DiscussionRepository = Depends(DiscussionRepository),
) -> CreateDiscussionResponse:
    discussion = await discussion_repo.create_discussion(
        discussion=Discussion.create(
            topic_id=q.topic_id.bytes,
        )
    )

    return CreateDiscussionResponse(
        id=discussion.id,
    )
