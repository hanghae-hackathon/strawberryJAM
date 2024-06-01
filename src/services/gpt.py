from fastapi import Depends

from typing import Dict, Iterator
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    BaseMessageChunk,
)

ChatMessage = SystemMessage | HumanMessage | AIMessage

from src.config import ConfigTemplate, get_config

memory_pool = {}
question_pool = {}


def get_question(discussion_id: str, question_num: int) -> str | None:
    return question_pool.get(discussion_id, None)[f"question_{question_num}"]


def create_question(discussion_id: str, questions: dict) -> None:
    question_pool[discussion_id] = questions


def get_memory(discussion_id: str) -> ConversationBufferMemory | None:
    return memory_pool.get(discussion_id, None)


def create_memory(discussion_id: str):
    memory_pool[discussion_id] = ConversationBufferMemory()


def get_or_create_memory(discussion_id: str) -> ConversationBufferMemory:
    """discussion_id가 존재하면 메모리를 리턴, 존재하지 않으면 메모리를 새롭게 생성하고 리턴합니다."""
    if discussion_id not in memory_pool:
        create_memory(discussion_id)
    return get_memory(discussion_id)


def split_questions(big_questions) -> Dict:
    """
    입력 문자열을 질문별로 잘라 리스트에 저장하는 함수.

    Args:
    big_questions (str): 전체 질문 문자열

    Returns:
    dict: 개별 질문이 저장된 리스트
    """
    # 질문을 구분하는 패턴 정의
    try:
        questions = {
            f"question_{i}": big_questions.split(f"<질문_{i}>")[1]
            .split(f"</질문_{i}>")[0]
            .strip()
            for i in range(1, 4)
        }
    except:
        questions = {"question": big_questions}

    return questions


class GPTService:
    def __init__(self, config_template: ConfigTemplate = Depends(get_config)):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            streaming=True,
            openai_api_key=config_template.OPENAI_API_KEY,
            temperature=0.5,
        )
    
    # 맨 처음 호출될 함수
    def init_memory(self, discussion_id: str, system_message: str) -> None:
        """
        메모리 생성 -> system_prompt 저장 (big main question 생성)

        Args:
            discussion_id (str): _description_
            system_message (str): _description_
        """

        create_memory(discussion_id)
        self.generate_big_question(discussion_id, system_message)
        return None

    def chat(self, messages: list[ChatMessage]) -> Iterator[BaseMessageChunk]:
        """
            채팅이 진행됩니다. 유저의 질문을 바탕으로 다음 질문을 생성합니다.

        Args:
            discussion_id (str | int): _description_
            user_response (str): _description_
        """
        system_message = SystemMessage(
            content="위 뉴스기사를 보고 이해도를 판단할 수 있을 법한 질문 3개만 해줘.\n 너가 답변은 하지 말고.",
        )
        print(messages)
        return self.llm.stream(input=[system_message] + messages)

    def reload_conversation(self, discussion_id: str) -> ConversationChain:
        """chatting이 가능한 chain을 생성하여 리턴합니다."""
        memory = get_or_create_memory(discussion_id)
        return ConversationChain(llm=self.llm, memory=memory)

    def generate_big_question(self, discussion_id: str, system_message: str) -> None:
        """
        전달된 system_messages를 기반으로 main questions 생성.(memory에 저장만 해둠)
        llmchain 생성 -> 프롬프트를 기반으로 생성

        생성된 questions들은 추후 사용되어야 하므로 따로 저장합니다.

        Args:
            discussion_id (str): _description_
            system_message (str): 토픽, 뉴스 기사
        """

        conversation = self.reload_conversation(discussion_id)
        big_questions = conversation.predict(input=system_message)
        splitted_big_questions = split_questions(big_questions)

        create_question(discussion_id, splitted_big_questions)

        return None


# if __name__ == "__main__":
#     init_memory(1, "이것은 기사입니다. ... 사용자의 이해도를 측정하기 위한 질문을 3가지 생성하세요 ...")
#     breakpoint()
#     res = chat(1, None, "첫 번째 유저 질문입니다 ?")
#     breakpoint()
