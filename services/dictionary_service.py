"""
Сервис для работы со справочниками
"""
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from config.settings import settings


@dataclass
class Dictionaries:
    """Справочники системы"""
    captains: list[str] = field(default_factory=list)
    boats: list[str] = field(default_factory=list)
    programs: list[str] = field(default_factory=list)
    piers: list[str] = field(default_factory=list)


class DictionaryService:
    """Сервис для загрузки и работы со справочниками"""
    
    def __init__(self):
        self._dictionaries: Optional[Dictionaries] = None
    
    def load(self) -> Dictionaries:
        """Загрузить справочники из YAML файла"""
        file_path = settings.dictionaries_file
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл справочников не найден: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self._dictionaries = Dictionaries(
            captains=data.get('captains', []),
            boats=data.get('boats', []),
            programs=data.get('programs', []),
            piers=data.get('piers', [])
        )
        
        return self._dictionaries
    
    def reload(self) -> Dictionaries:
        """Перезагрузить справочники"""
        return self.load()
    
    @property
    def dictionaries(self) -> Dictionaries:
        """Получить справочники (с ленивой загрузкой)"""
        if self._dictionaries is None:
            self.load()
        return self._dictionaries
    
    @property
    def captains(self) -> list[str]:
        """Получить список капитанов"""
        return self.dictionaries.captains
    
    @property
    def boats(self) -> list[str]:
        """Получить список лодок"""
        return self.dictionaries.boats
    
    @property
    def programs(self) -> list[str]:
        """Получить список программ"""
        return self.dictionaries.programs
    
    @property
    def piers(self) -> list[str]:
        """Получить список пирсов"""
        return self.dictionaries.piers


# Глобальный экземпляр сервиса
dictionary_service = DictionaryService()
