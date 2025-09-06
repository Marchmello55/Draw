from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def add_code_button() -> InlineKeyboardMarkup:
    """
    кнопка добавление
    :param data:
    :return:
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить код",
        callback_data="add_code"
    )
    builder.button(
        text="Мои коды",
        callback_data="my_codes"
    )
    builder.adjust(1)

    return builder.as_markup()


async def get_bonus() -> InlineKeyboardMarkup:
    """
    кнопка добавление
    :param data:
    :return:
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Получить промокод",
        callback_data="get_promo"
    )
    builder.adjust(1)

    return builder.as_markup()