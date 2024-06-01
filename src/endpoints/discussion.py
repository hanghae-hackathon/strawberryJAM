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
    
    wordpaper_prompt = (
        "Assume you are the professional Korean Professor, who is writing Korean Vocabulary book. Your task is following:\n "
        "1. 뉴스기사에서 19세 이상 한국인 성인들이 어려워할 수 있는 단어나 익숙하지 않은 단어를 찾아주세요. (의학, 경제 등 전문 분야에 해당하는 단어) 난이도 순으로 최대 6개만 선정하세요. (단어에 대한 난이도를 점수로 매긴 뒤, 난이도가 높게 책정된 단어만 포함하세요. 점수는 출력하지 않습니다.)\n "
        "2. 또한 구어체보다는 문어체로 많이 쓰이는 단어와 구문도 포함시켜주세요.\n "
        "3. 각 단어와 구문의 의미를 뉴스기사와 주어진 문맥에 맞추어 작성해주세요.\n "
        "4. 단어장의 포맷은 다음과 같은 마크다운 포맷을 유지해주세요: \n "
        "예시는 다음과 같습니다. 반드시 markdown 포맷으로 생성하세요.:\n "
        "#####제로섬 경쟁\n "
        "- 승자의 득점과 패자의 실점을 합한 총계가 제로가 되는 스포츠나 게임을 의미합니다.\n "
        "#####위약군\n "
        "- 환자에게 심리적 효과를 얻도록 하려고 주는 가짜 약을 먹은 집단을 의미하는 의학 용어입니다.\n "
        "짧은 뉴스기사 예시: \n"
        "국제 올림픽 위원회는 최근 제로섬 경쟁에 대한 우려를 표하며, 모든 선수들이 상호 존중의 정신으로 경기에 임할 것을 강조했습니다. 한편, 최신 임상 실험 결과에 따르면 위약군에서도 실제 약품을 복용한 그룹과 유사한 개선 효과가 나타나, 위약 효과의 심리적 기여가 크다는 점이 확인되었습니다."
        "다음은 실제 뉴스기사입니다. 다음 기사를 바탕으로 task를 수행해주세요. 그리고 단어만 출력해주세요.\n"
        f"{ topic.description }"
        
    )
    
    final_wordpaper = ""
    
    wordpapers = gpt_service.chat(messages=[HumanMessage(content=wordpaper_prompt)])
    
    for wordpaper in wordpapers:
        final_wordpaper += wordpaper.content

    init_prompt = (
        f"지금부터 당신은 성인을 위한 토론 능력과 디지털 문해력 향상을 위한 토의를 진행하는 전문가입니다.\n "
        "다음 뉴스기사를 토대로, 사용자가 뉴스 기사를 충분히 이해했는지, 핵심 쟁점을 바탕으로 토의를 진행할 수 있는지, 비판적으로 사고하는 능력을 가지고 있는지를 판단하려고 합니다.\n "
        "질문은 토의에 적절한 질문이어야 합니다. 다시 말하면, 너무 세부사항을 물어보는 구체적인 질문은 아니면서, 충분히 기사를 이해하고 있는지, 비판적이고 논리적인 사고를 하고 있는지를 판단하는 적절한 질문이어야 합니다.\n"
        "질문에 대한 답변은 반드시 주어진 기사에서 찾아볼 수 있어야 합니다. Only follow my instruction.\n "
        "뉴스기사 전문: \n"
        "```\n"
        f"{ topic.description }"
        "``` \n"
        "My instruction: \n"
        "먼저, 유저는 위 뉴스기사를 바탕으로 요약문을 작성해서 제공할거야. 이제, 'Ready to Debate'만 출력해. \n"
        "다른 말은 출력하지 마세요. \n"
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
            "wordpaper": final_wordpaper,
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
