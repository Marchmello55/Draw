from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

from handlers.start import get_id
from keyboards import buttons as bt
from database import requests as rq

import logging

router = Router()


class CodeData(StatesGroup):
    code = State()

@router.callback_query(F.data == "add_code")
async def press_add_code(callback: CallbackQuery, state: FSMContext):
    """

    :param callback:
    :param state:
    :return:
    """
    logging.info("press_add_code")
    await callback.answer()
    await callback.message.edit_text(text="введите код со скретч-карты")
    await state.set_state(state=CodeData.code)



@router.callback_query(F.data == "my_codes")
async def my_codes(callback: CallbackQuery, state: FSMContext):
    """
    Вывод кодов пользователя
    :param callback:
    :param state:
    :return:
    """
    logging.info("my_codes")
    message_id, chat_id = await get_id(state)
    codes = await rq.get_codes_by_user(tg_id=int(chat_id))
    if len(codes) > 0:
        code_text = "\n".join([i.code for i in codes])
        await callback.message.edit_text(text=f"Ваши введенные коды:\n{code_text}",
                                    reply_markup=await bt.add_code_button())
    else:await callback.message.edit_text(text="У вас нет введенных кодов",
                                    reply_markup=await bt.add_code_button())


@router.message(F.text, StateFilter(CodeData.code))
async def add_code(message: Message, bot: Bot, state: FSMContext):
    logging.info("add_code")
    message_id, chat_id = await get_id(state)
    smth = await rq.update_tg_id_code(tg_id=int(message.from_user.id), code=message.text)
    codes = await rq.get_codes_by_user(int(message.from_user.id))
    if str(smth) == "2":
        await bot.edit_message_text(message_id=message_id,
                                    chat_id=chat_id,
                                    text="Этот код уже был зарегистрирован ранее."
                                         " Пожалуйста, проверьте правильность ввода или используйте другой код.",
                                    reply_markup=await bt.add_code_button())
        await message.delete()
    elif smth:
        s = len(codes)
        cod = '1 код'
        n1 = 'кодов'
        n2 = 'код'
        n3 = 'кода'
        if s >= 0:
            if s == 0:
                cod = str(s) + ' ' + n1
            elif s % 100 >= 10 and s % 100 <= 20:
                cod = str(s) + ' ' + n1
            elif s % 10 == 1:
                cod = str(s) + ' ' + n2
            elif s % 10 >= 2 and s % 10 <= 4:
                cod = str(s) + ' ' + n3
            else:
                cod = str(s) + ' ' + n1
        await bot.edit_message_text(message_id=message_id,
                                    chat_id=chat_id,
                                    text=f"Код успешно добавлен! Вы добавили {cod} для участия в розыгрыше."
                                         f" Вы можете добавить ещё один код, нажав на кнопку ниже",
                                    reply_markup=await bt.add_code_button())
        await message.delete()

    else:
        await bot.edit_message_text(message_id=message_id,
                                    chat_id=chat_id,
                                    text="Такого кода не найдено в системе."
                                         " Проверьте правильность ввода — возможно, была допущена опечатка."
                                         " Вы можете ввести код ещё раз"
                                    , reply_markup=await bt.add_code_button())
        await message.delete()