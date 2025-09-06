from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from database.base import Base, engine


class User(Base):
    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None]
    number: Mapped[int]


class Code(Base):
    code: Mapped[str] = mapped_column(String, primary_key=True)
    tg_id: Mapped[int | None]


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

