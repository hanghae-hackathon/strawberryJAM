import asyncio
import json
import uuid
from fastapi import Depends, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from src.models.message import Message
from src.services.gpt import GPTService
from src.services.message import MessageService

from langchain.schema.messages import HumanMessage, AIMessage

ws = FastAPI()

ws.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@ws.websocket("/discussions")
async def websocket_endpoint(
    websocket: WebSocket,
    message_service: MessageService = Depends(MessageService),
    gpt_service: GPTService = Depends(GPTService),
):
    await websocket.accept()
    while True:
        data = json.loads(await websocket.receive_text())

        user_message = Message.create(
            role="user",
            message=data["message"],
            discussion_id=uuid.UUID(data["discussion_id"]).bytes,
        )

        await message_service.create_message(user_message)

        messages = await message_service.get_messages_by_discussion_id(
            discussion_id=uuid.UUID(data["discussion_id"]).bytes
        )

        user_message_count = len(
            [message for message in messages if message.role == "user"]
        )

        stream = gpt_service.chat(
            messages=[
                (
                    HumanMessage(
                        content=message.message,
                    )
                    if message.role == "user"
                    else AIMessage(
                        content=message.message,
                    )
                )
                for message in messages
            ]
        )

        ai_message = await message_service.create_message(
            Message.create(
                role="bot",
                message="",
                discussion_id=uuid.UUID(data["discussion_id"]).bytes,
            ),
        )

        temp = ""

        for chunk in stream:
            c = chunk.content
            temp += c
            await websocket.send_text(
                json.dumps(
                    {
                        "id": str(ai_message.id),
                        "message": c,
                        "role": "bot",
                    }
                )
            )
            await asyncio.sleep(0.01)

        await message_service.update_message(
            Message(
                id=ai_message.id,
                role="bot",
                message=temp,
                discussion_id=uuid.UUID(data["discussion_id"]).bytes,
            ),
        )

        messages = await message_service.get_messages_by_discussion_id(
            discussion_id=uuid.UUID(data["discussion_id"]).bytes
        )

        if user_message_count == 4:
            prompt = """이제 유저와 전문가의 토의 내용을 바탕으로 유저에게 토의내용에 대한 피드백을 제공하고자 합니다.
피드백은 먼저 유저의 답변에 대한 칭찬으로 시작해야합니다. 잘한 점을 2가지 먼저 언급하세요.
그 다음, 개선해야할 점을 3가지를 분석하고 제시하세요.

다음 사항들에 주의하여 피드백을 구성하세요.
- 개선해야할 점으로 제시하는 피드백은 유저의 '논리력' 및 '문해력'을 증진시키는 데 도움이 되어야 합니다는 것에 주의하세요.
- 개선해야할 점을 제시할 때 추가적으로, '앞으로 {something1} 능력을 향상시키고 싶으시다면 {something2} 과 같이 말하거나, {something3} 을 생각해보시길 바랍니다' 와 같이 분석적이고 미래지향적인 방향으로 제시하세요. (주어진 문장의 포맷을 사용하되, 변형해서 사용하세요.)
- 또한, 잘 한점과 개선해야할 점을 언급할 때는, 직접 유저의 답변을 인용하세요. 신뢰성에 도움이 됩니다.
- 피드백의 마지막으로, 전체적인 토의의 품질과 수준을 고려하여 10점 만점의 점수를 생성하세요.
- 각 피드백은 충분히, 풍부하게 길게 생성하세요.

잘 한점은 '## 잘한 점' 이라는 문구로 시작하여 답변하고,
개선해야할 점은 '## 개선해야 할 점'이라는 문구로 시작하여 생성하세요.
점수는 '## 모의 토의 점수'라는 문구로 시작하여 생성하세요. 점수를 매길 때, 이전에 평가했던 토론 점수를 기반으로 점수를 매기세요.
즉, 지금까지의 토의에서, 유저의 답변이 주어진 질문과 관련이 없으면 1-2점, 약간만 관련이 있거나 논리가 부족하다면 3-7점, 충분하다면 8-10점을 부여하세요. 만점은 10점입니다.
각 파트별 사이에는 줄바꿈을 두번, 즉 '\n\n'을 생성하세요."""

            ai_message = await message_service.create_message(
                Message.create(
                    role="bot",
                    message="",
                    discussion_id=uuid.UUID(data["discussion_id"]).bytes,
                ),
            )

            stream = gpt_service.chat(
                messages=[
                    (
                        HumanMessage(
                            content=prompt,
                        )
                    ),
                ]
            )

            temp = ""

            for chunk in stream:
                c = chunk.content
                temp += c
                await websocket.send_text(
                    json.dumps(
                        {
                            "id": str(ai_message.id),
                            "message": c,
                            "role": "bot",
                        }
                    )
                )
                await asyncio.sleep(0.01)

            await message_service.update_message(
                Message(
                    id=ai_message.id,
                    role="bot",
                    message=temp,
                    discussion_id=uuid.UUID(data["discussion_id"]).bytes,
                ),
            )

            break

        await websocket.send_text(
            json.dumps(
                {
                    "message": f"질문: ({4 - user_message_count}/3)",
                    "role": "system",
                }
            )
        )
