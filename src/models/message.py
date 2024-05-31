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

if typing.TYPE_CHECKING:
    from .discussion import Discussion


class Message(Base):
    __tablename__ = "messages"

    id = mapped_column(BLOB, primary_key=True, default=lambda: uuid.uuid4().bytes)
    role = mapped_column(String, nullable=False)
    message = mapped_column(Text, nullable=False)
    discussion_id = mapped_column(BLOB, ForeignKey("discussions.id"), nullable=False)

    discussion: Mapped["Discussion"] = relationship(
        "Discussion", back_populates="messages"
    )

    @classmethod
    def create(
        cls,
        role: str,
        message: str,
        discussion_id: bytes,
    ) -> "Message":
        return cls(
            role=role,
            message=message,
            discussion_id=discussion_id,
        )
