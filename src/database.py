from src.config import ConfigTemplate, get_config

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class SqlaEngine:
    def __init__(
        self,
        config: ConfigTemplate,
    ) -> None:
        self._engine = create_async_engine(config.db_uri, logging_name="sa_logger")

    @property
    def engine(self):
        return self._engine

    @property
    def session(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            bind=self._engine,
        )


async def get_db(
    config: ConfigTemplate = Depends(get_config),
):
    session = SqlaEngine(config).session()

    if session is None:
        raise Exception("session is not connected")
    try:
        yield session
    finally:
        await session.close()
