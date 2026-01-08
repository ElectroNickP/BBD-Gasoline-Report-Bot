"""
Сервис для работы с пользователями и авторизацией
"""
import yaml
from typing import Optional
from dataclasses import dataclass

from config.settings import settings


@dataclass
class AllowedUser:
    """Пользователь с доступом к боту"""
    telegram_id: int
    name: str


class UserService:
    """Сервис авторизации пользователей по whitelist"""
    
    def __init__(self):
        self._users: dict[int, AllowedUser] = {}
        self._loaded = False
    
    def load(self) -> None:
        """Загрузить список пользователей из YAML файла"""
        file_path = settings.allowed_users_file
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл пользователей не найден: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self._users.clear()
        for user_data in data.get('users', []):
            user = AllowedUser(
                telegram_id=user_data['telegram_id'],
                name=user_data.get('name', 'Unknown')
            )
            self._users[user.telegram_id] = user
        
        self._loaded = True
    
    def reload(self) -> None:
        """Перезагрузить список пользователей"""
        self.load()
    
    def is_allowed(self, telegram_id: int) -> bool:
        """Проверить, разрешён ли пользователю доступ"""
        if not self._loaded:
            self.load()
        
        # Если ID = 0, разрешаем всем (для тестирования)
        if 0 in self._users:
            return True
        
        return telegram_id in self._users
    
    def get_user(self, telegram_id: int) -> Optional[AllowedUser]:
        """Получить данные пользователя"""
        if not self._loaded:
            self.load()
        return self._users.get(telegram_id)
    
    def get_all_users(self) -> list[AllowedUser]:
        """Получить всех пользователей"""
        if not self._loaded:
            self.load()
        return list(self._users.values())


# Глобальный экземпляр сервиса
user_service = UserService()
