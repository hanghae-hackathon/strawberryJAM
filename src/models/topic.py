import typing
from typing import List
import uuid
from .base import Base
from sqlalchemy import BLOB, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if typing.TYPE_CHECKING:
    from .discussion import Discussion


class Topic(Base):
    __tablename__ = "topics"

    id = mapped_column(BLOB, primary_key=True, default=lambda: uuid.uuid4().bytes)
    title = mapped_column(String, nullable=False)
    description = mapped_column(Text, nullable=False)
    image = mapped_column(Text)

    discussions: Mapped[List["Discussion"]] = relationship(
        "Discussion", back_populates="topic"
    )

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
    ) -> "Topic":
        return cls(
            title=title,
            description=description,
        )
