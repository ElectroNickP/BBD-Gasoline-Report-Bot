"""
Настройки приложения
"""
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


@dataclass
class Settings:
    """Настройки приложения"""
    
    # Telegram Bot
    bot_token: str = os.getenv("BOT_TOKEN", "8227838413:AAF5HK0zkfRNtDij1HaODxmKDYI-4XqoAW4")
    
    # Database
    database_url: str = f"sqlite+aiosqlite:///{DATA_DIR}/gasoline.db"
    
    # Config files
    dictionaries_file: Path = CONFIG_DIR / "dictionaries.yaml"
    allowed_users_file: Path = CONFIG_DIR / "allowed_users.yaml"
    
    def __post_init__(self):
        # Создаём директорию для данных
        DATA_DIR.mkdir(exist_ok=True)


settings = Settings()
