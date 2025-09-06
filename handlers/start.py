from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup


from config_data.config import load_config, Config
from keyboards import buttons as bt
from database import requests as rq

import logging

router = Router()
config: Config = load_config()


class UserData(StatesGroup):
    number = State()


class LastMessage(StatesGroup):
    message_id = State()
    chat_id = State()


async def get_id(state: FSMContext):
    state_data = await state.get_data()
    message_id = state_data.get("message_id")
    chat_id = state_data.get("chat_id")
    return message_id, chat_id


@router.message(F.text == "Главное меню")
@router.message(CommandStart())
async def process_press_start(message: Message, bot: Bot, state: FSMContext):
    """
    Проверка на наличие пользователя в бд и соотв действие
    :param message:
    :param bot:
    :param state:
    :return:
    """
    logging.info("process_press_start")
    state_data = await state.get_data()
    message_id = state_data.get("message_id")
    chat_id = state_data.get("chat_id")

    # Пытаемся удалить предыдущее сообщение бота

    if message_id and chat_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
    check_ = await rq.chack_user(tg_id=message.from_user.id)
    if not check_:
        new_message = await message.answer(text=f"Добро пожаловать, {message.from_user.first_name}!"
                                                " Для участия в розыгрыше необходимо пройти регистрацию."
                                                " Пожалуйста, поделитесь вашим номером телефона в формате: 89887772211")
        await state.set_state(state=UserData.number)
    else:
        new_message = await message.answer(text=f"Здравствуйте, {message.from_user.first_name}",
                                           reply_markup=await bt.add_code_button())
    try:
        await message.delete()
    except:
        pass
    await state.update_data(
        message_id=new_message.message_id,
        chat_id=new_message.chat.id
    )


@router.message(F.text, StateFilter(UserData.number))
async def add_user(message: Message, bot: Bot, state: FSMContext):
    logging.info("add_user")
    message_id, chat_id = await get_id(state)
    if not message.text.isdigit():
        await bot.edit_message_text(message_id=message_id, chat_id=chat_id, text="Неверный формат номера. "
                                                                                 "Пожалуйста, введите номер, используя только цифры "
                                                                                 "(11 цифр без пробелов и других символов)")
        await message.delete()
        return
    else:
        if len(message.text) != 11:
            await bot.edit_message_text(message_id=message_id, chat_id=chat_id, text="В номере телефона должно быть 11 цифр."
                                                                                     " Пожалуйста, проверьте и введите номер ещё раз")
            await message.delete()
            return
        if not await rq.chack_user_number(number=int(message.text)):
            await bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                        text="Этот номер телефона уже зарегистрирован в системе."
                                             " Пожалуйста, используйте другой номер для регистрации")
            await message.delete()
            return
        await rq.add_user({"tg_id": int(message.from_user.id), "username": message.from_user.username, "number":int(message.text)})
        await bot.edit_message_text(message_id=message_id,
                                    chat_id=chat_id,
                                    text="Регистрация номера телефона успешно завершена."
                                         " Для участия в розыгрыше необходимо добавить код со скретч-карты"
                                    , reply_markup=await bt.add_code_button())
        await message.delete()
