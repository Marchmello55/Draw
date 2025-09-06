from aiogram.filters import Filter
from aiogram import types
import os
from functools import lru_cache
from typing import Union, List


class HasAccessFilter(Filter):
    def __init__(self, access_level: Union[str, List[str]] = "ADMIN"):
        """
        Фильтр для проверки доступа пользователя

        :param access_level: Уровень доступа или список уровней
        Примеры: "ADMIN", "MODERATOR", ["ADMIN", "MODERATOR"]
        """
        if isinstance(access_level, str):
            self.access_levels = [access_level.upper()]
        else:
            self.access_levels = [level.upper() for level in access_level]

    @staticmethod
    @lru_cache(maxsize=10)
    def _get_cached_ids(env_var_name: str) -> tuple:
        """
        Получает и кэширует ID из переменной окружения

        :param env_var_name: Имя переменной окружения
        :return: Кортеж с ID
        """
        ids_str = os.getenv(env_var_name, '')
        if not ids_str:
            return tuple()

        try:
            # Преобразуем "123, 456, 789" в (123, 456, 789)
            return tuple(int(id.strip()) for id in ids_str.split(','))
        except ValueError:
            return tuple()

    async def __call__(self, message: types.Message) -> bool:
        """
        Проверяет, имеет ли пользователь доступ
        """
        user_id = message.from_user.id

        for access_level in self.access_levels:
            if await self._check_access_level(user_id, access_level):
                return True

        return False

    async def _check_access_level(self, user_id: int, access_level: str) -> bool:
        """Проверяет конкретный уровень доступа"""
        if access_level == "ADMIN":
            return self._check_admin_access(user_id)
        elif access_level == "MODERATOR":
            return self._check_moderator_access(user_id)
        elif access_level == "SUPPORT":
            return self._check_support_access(user_id)
        else:
            # Для кастомных уровней доступа
            return self._check_custom_access(user_id, access_level)

    def _check_admin_access(self, user_id: int) -> bool:
        """Проверяет доступ администратора"""
        admin_ids = self._get_cached_ids('ADMIN_ID')
        support_id = os.getenv('SUPPORT_ID')

        # Проверяем ADMIN_IDS
        if user_id in admin_ids:
            return True

        # Проверяем SUPPORT_ID для обратной совместимости
        if support_id and support_id.isdigit() and user_id == int(support_id):
            return True

        return False

    def _check_moderator_access(self, user_id: int) -> bool:
        """Проверяет доступ модератора"""
        moderator_ids = self._get_cached_ids('MODERATOR_ID')
        return user_id in moderator_ids

    def _check_support_access(self, user_id: int) -> bool:
        """Проверяет доступ поддержки"""
        support_ids = self._get_cached_ids('SUPPORT_ID')
        return user_id in support_ids

    def _check_custom_access(self, user_id: int, role_name: str) -> bool:
        """Проверяет кастомный уровень доступа"""
        role_ids = self._get_cached_ids(f'{role_name}_ID')
        return user_id in role_ids