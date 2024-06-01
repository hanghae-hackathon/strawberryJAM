import uuid
from .base import Base
from sqlalchemy import (
    BLOB,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing
from typing import List


if typing.TYPE_CHECKING:
    from .topic import Topic
    from .message import Message


class Discussion(Base):
    __tablename__ = "discussions"

    id = mapped_column(BLOB, primary_key=True, default=lambda: uuid.uuid4().bytes)
    topic_id = mapped_column(BLOB, ForeignKey("topics.id"), nullable=False)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="discussions")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="discussion"
    )

    @classmethod
    def create(
        cls,
        topic_id: bytes,
    ) -> "Discussion":
        return cls(
            topic_id=topic_id
        )
