from aiogram import Router, Bot, F
from aiogram.types import Message,  ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command


from config_data.config import load_config, Config
from database import requests as rq
from filter.access_filter import HasAccessFilter

import logging
import tempfile
import os

router = Router()
config: Config = load_config()


class AddFile(StatesGroup):
    waiting_for_file = State()


@router.message(Command("add_file"), HasAccessFilter("ADMIN"))
async def add_current_codes(message: Message, state: FSMContext):
    """
    Переход в состояние для добавления рабочих кодов
    """
    logging.info("add_current_codes")
    await message.delete()

    await message.answer(
        "📁 Пожалуйста, отправьте файл .txt с кодами.\n\n"
        "Файл должен содержать код разделенный пробелом или новой строчкой.\n"
        "Пример содержимого:\n"
        "CODE123\n"
        "CODE456 "
        "CODE789"
    )

    await state.set_state(AddFile.waiting_for_file)


@router.message(StateFilter(AddFile.waiting_for_file), F.content_type == ContentType.DOCUMENT)
async def process_code_file(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка полученного файла с кодами
    """
    logging.info("process_code_file")
    pass
    # Проверяем, что файл имеет расширение .txt
    if not message.document.file_name.endswith('.txt'):
        await message.answer("❌ Файл должен быть в формате .txt")

        return

    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            temp_filename = tmp_file.name

        # Скачиваем файл
        await bot.download(
            message.document,
            destination=temp_filename
        )

        # Читаем и парсим файл
        codes = await parse_codes_from_file(temp_filename)

        if not codes:
            await message.answer("❌ Файл пуст или содержит некорректные данные")
            return

        # Добавляем коды в базу
        added_count = await rq.add_codes_bulk(codes)

        # Отправляем результат
        await message.answer(
            f"✅ Обработка завершена!\n\n"
            f"• Всего кодов в файле: {len(codes)}\n"
            f"• Успешно добавлено: {added_count}\n"
        )

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        await message.answer(f"❌ Произошла ошибка при обработке файла: {e}")

    finally:
        # Очищаем состояние и удаляем временный файл
        await state.clear()
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


@router.message(StateFilter(AddFile.waiting_for_file))
async def wrong_file_type(message: Message):
    """
    Обработка неправильного типа сообщения в состоянии
    """
    logging.info("wrong_file_type")
    await message.delete()
    await message.answer(
        "❌ Пожалуйста, отправьте файл .txt с кодами.\n\n"
        "Если вы отправили не файл, отправьте текстовый файл "
        "с расширением .txt, содержащий коды построчно."
    )


async def parse_codes_from_file(file_path: str) -> list:
    """
    Парсит коды из текстового файла
    """
    logging.info("parse_codes_from_file")
    codes = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Очищаем строку от  переносов
                code = line.replace("\n", " ")

                # Пропускаем пустые строки
                if not code:
                    continue

                code = code.split(" ")
                # Проверяем, что код не пустой после очистки
                if code:
                    codes.extend(code)
                    codes.remove("")

        logging.info(f"Parsed {len(codes)} codes from file")
        return codes

    except Exception as e:
        logging.error(f"Error parsing file: {e}")
        return []
