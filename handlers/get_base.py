from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from database import database as db
from config_data.config import load_config, Config
from database import requests as rq
from filter.access_filter import HasAccessFilter

import logging

router = Router()
config: Config = load_config()


@router.message(Command("get_base"), HasAccessFilter("ADMIN"))
async def get_base(message: Message, bot: Bot):
    logging.info("get_base")
    data = await rq.get_all_users()
    data_code = await rq.get_all_codes()
    await db.create_excel()
    for i in data:
        await db.add_row("Users", i)
    for i in data_code:
        await db.add_row("Codes", i)
    document = FSInputFile("example.xlsx")
    await bot.send_document(chat_id=message.from_user.id, document=document)
    await message.delete()
