import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import async_session, connection
from database.models import User, Code

import asyncio

@connection
async def add_user(user_data: dict, session: AsyncSession):
    logging.info("add_user")
    user = await session.scalar(select(User).where(User.tg_id == user_data["tg_id"]))
    if not user:
        user = User(**user_data)
    session.add(user)
    await session.commit()

@connection
async def chack_user(tg_id: int, session: AsyncSession):
    logging.info("chack_user")
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user:return False
    else:return  True

@connection
async def chack_user_number(number: int, session: AsyncSession):
    logging.info("chack_user_number")
    user = await session.scalar(select(User).where(User.number == number))
    if not user:
        return True
    else:
        return False


@connection
async def get_user_by_id(tg_id: int, session: AsyncSession):
    logging.info("get_user_by_id")
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user


@connection
async def get_all_users(session: AsyncSession):
    logging.info("get_all_users")
    users = await session.scalars(select(User))
    return [[i.tg_id, i.username, i.number] for i in users]


@connection
async def get_all_codes(session: AsyncSession):
    logging.info("get_all_codes")
    codes = await session.scalars(select(Code))
    return [[i.tg_id, i.code] for i in codes]


@connection
async def update_tg_id_code(tg_id: int, code: str, session: AsyncSession):
    logging.info("update_tg_id_code")
    code = await session.scalar(select(Code).where(Code.code == code))
    if not code:
        return False
    elif code.tg_id != None:
        return 2
    else:
        code.tg_id = tg_id
        await session.commit()
        return True


@connection
async def get_codes_by_user(tg_id: int, session: AsyncSession):
    logging.info("get_codes_by_user")
    codes = await session.scalars(select(Code).where(Code.tg_id == tg_id))
    return [i for i in codes]


@connection
async def get_code_to_draw(session: AsyncSession):
    logging.info("get_code_to_draw")
    codes = await session.scalars(select(Code).where(Code.tg_id != None))
    return [i for i in codes]



@connection
async def add_code(code_str: str, session: AsyncSession):
    logging.info("add_code")
    # Проверяем, существует ли уже такой код
    existing_code = await session.scalar(select(Code).where(Code.code == code_str))
    if existing_code:
        logging.warning(f"Code {code_str} already exists")
        return False

    # Создаем новый код
    new_code = Code(code=code_str, tg_id=None)
    session.add(new_code)
    await session.commit()
    logging.info(f"Code {code_str} added successfully")
    return True


@connection
async def add_codes_bulk(codes_list: list[str], session: AsyncSession) -> int:
    """
    Массовое добавление кодов (опционально, для оптимизации)
    """
    logging.info(f"add_codes_bulk: {len(codes_list)} codes")
    await session.execute(delete(Code))
    new_codes = [Code(code=code_value, tg_id=None) for code_value in codes_list]
    session.add_all(new_codes)
    await session.commit()
    logging.info(f"Successfully replaced all codes. New count: {len(codes_list)}")
    return len(codes_list)

