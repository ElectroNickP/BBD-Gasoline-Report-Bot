"""
Состояния FSM для ConversationHandler
"""
from enum import IntEnum, auto


class ReportStates(IntEnum):
    """Состояния заполнения отчёта"""
    
    # Выбор из справочников
    CAPTAIN = auto()
    BOAT = auto()
    PROGRAM = auto()
    PRIVATE_PROGRAM = auto()  # Программа для приватного тура (если выбрана N/A)
    PIER = auto()
    
    # Даты
    DEPARTURE_DATE = auto()
    RETURN_DATE = auto()
    REFILL_DATE = auto()
    
    # Числовые данные
    MAX_SPEED = auto()
    GASOLINE_REFUEL = auto()
    TOTAL_GASOLINE = auto()
    GASOLINE_USED = auto()
    
    # Опциональные поля
    MILEAGE = auto()
    MILEAGE_PHOTO = auto()
    BILL_PHOTO = auto()
    
    # Подтверждение
    CONFIRM = auto()
