from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import load_config, Config
from database import requests as rq
from filter.access_filter import HasAccessFilter
from keyboards import buttons as bt

import logging
import random, asyncio

router = Router()
config: Config = load_config()


@router.message(Command("draw"), HasAccessFilter("ADMIN"))
async def draw(message: Message, bot: Bot, state: FSMContext):
    logging.info("draw")

    data = await rq.get_code_to_draw()
    number = await get_random_number_async(min_val=0, max_val=len(data)-1)
    user_data = await rq.get_user_by_id((data[number]).tg_id)
    if user_data.username:
        user ="@" + user_data.username
    else:
        user = f"<a href='tg://user?id={data[number].tg_id}'>Победитель</a>"
    await bot.send_message(chat_id=(data[number]).tg_id,
                           text=f"""🎊{user}, поздравляем Вас! 🎊

Ваша удача улыбнулась сегодня💫 

Ждем Вас в нашей чайной Met Tea на 1905 года для вручения приза📱 в любое удобное для Вас время🙌""",
                           parse_mode="HTML")
    await message.answer(f"Победитель розыгрыша: {user}",
                         parse_mode="HTML")
    users_all = await rq.get_all_users()
    for user_ in users_all:
        try:
            await bot.send_message(chat_id=user_[0],
                                   text=f"""  🎉 Настало время подвести итоги розыгрыша🎉 

    🍀Счастливым стал билет с кодом {data[number].code}🍀

    Поздравляем победителя {user}, поймавшего удачу за хвост💫🦊

    Спасибо, что участвовали в нашем розыгрыше❤️ 

    Нажмите на кнопку ниже, чтобы получить промо-код на скидку 10% на следующую покупку в чайной Met Tea  на 1905 года🫶""",
                                   reply_markup=await bt.get_bonus())
        except Exception as e:
            logging.info(f'{user_[0]} - {e}')
    await message.delete()


async def get_random_number_async(min_val: int, max_val: int) -> int:
    """
    Асинхронная версия функции получения случайного числа
    """
    return await asyncio.to_thread(random.randint, min_val, max_val)


@router.callback_query(F.data == 'get_promo')
async def get_promo(callback: CallbackQuery):
    await callback.message.edit_text(text='Ваш промо-код на скидку 10% на следующую покупку'
                                          ' в чайной Met Tea  на 1905 года🫶\n\n'
                                          '<b>Met_Tea_10</b>')
