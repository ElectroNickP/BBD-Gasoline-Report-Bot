"""
Сервис для работы с отчётами о топливе
"""
from datetime import date
from typing import Optional
from dataclasses import dataclass, field

from database.repository import report_repository
from database.models import Report


@dataclass
class ReportData:
    """Данные отчёта для создания"""
    telegram_user_id: int
    captain_name: str = ""
    boat_name: str = ""
    program_name: str = ""
    private_program: Optional[str] = None  # Маршрут для приватного тура (если program_name = N/A)
    departure_pier: str = ""
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    refill_date: Optional[date] = None
    max_speed: int = 0
    gasoline_refuel: float = 0.0
    total_gasoline: float = 0.0
    gasoline_used: float = 0.0
    gasoline_left: float = 0.0
    mileage_ride: Optional[float] = None
    mileage_photo_id: Optional[str] = None
    bill_photo_id: Optional[str] = None
    
    def is_complete(self) -> bool:
        """Проверить, заполнены ли все обязательные поля"""
        return all([
            self.captain_name,
            self.boat_name,
            self.program_name,
            self.departure_pier,
            self.departure_date,
            self.return_date,
            self.refill_date,
            self.max_speed > 0,
        ])
    
    def calculate_gasoline_left(self) -> None:
        """Автоматически рассчитать остаток топлива"""
        self.gasoline_left = self.total_gasoline - self.gasoline_used
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь для сохранения"""
        return {
            'telegram_user_id': self.telegram_user_id,
            'captain_name': self.captain_name,
            'boat_name': self.boat_name,
            'program_name': self.program_name,
            'private_program': self.private_program,
            'departure_pier': self.departure_pier,
            'departure_date': self.departure_date,
            'return_date': self.return_date,
            'refill_date': self.refill_date,
            'max_speed': self.max_speed,
            'gasoline_refuel': self.gasoline_refuel,
            'total_gasoline': self.total_gasoline,
            'gasoline_used': self.gasoline_used,
            'gasoline_left': self.gasoline_left,
            'mileage_ride': self.mileage_ride,
            'mileage_photo_id': self.mileage_photo_id,
            'bill_photo_id': self.bill_photo_id,
        }


class ReportService:
    """Сервис бизнес-логики для отчётов"""
    
    async def create_report(self, data: ReportData) -> Report:
        """Создать новый отчёт"""
        if not data.is_complete():
            raise ValueError("Not all required fields are filled")
        
        # Автоматический расчёт остатка
        data.calculate_gasoline_left()
        
        return await report_repository.create(data.to_dict())
    
    async def get_user_reports(
        self, 
        telegram_user_id: int, 
        limit: int = 10
    ) -> list[Report]:
        """Получить отчёты пользователя"""
        return await report_repository.get_by_user(telegram_user_id, limit)
    
    async def get_captain_reports(
        self, 
        captain_name: str, 
        limit: int = 10
    ) -> list[Report]:
        """Получить отчёты капитана"""
        return await report_repository.get_by_captain(captain_name, limit)
    
    async def get_last_user_report(
        self, 
        telegram_user_id: int
    ) -> Optional[Report]:
        """Получить последний отчёт пользователя"""
        return await report_repository.get_last_report_by_user(telegram_user_id)
    
    def format_report_summary(self, data: ReportData) -> str:
        """Форматировать сводку отчёта для предпросмотра"""
        # Формируем строку программы с учётом приватного тура
        program_line = f"🏝 *Program:* {data.program_name}"
        if data.private_program:
            program_line += f" → *{data.private_program}*"
        
        return f"""
📋 *Report Summary*

👨‍✈️ *Captain:* {data.captain_name}
🚤 *Boat:* {data.boat_name}
{program_line}
⚓ *Pier:* {data.departure_pier}

📅 *Departure:* {data.departure_date.strftime('%d.%m.%Y') if data.departure_date else '—'}
📅 *Return:* {data.return_date.strftime('%d.%m.%Y') if data.return_date else '—'}
📅 *Refill Date:* {data.refill_date.strftime('%d.%m.%Y') if data.refill_date else '—'}

⚡ *Max Speed:* {data.max_speed}
⛽ *Refuel:* {data.gasoline_refuel}
⛽ *Total:* {data.total_gasoline}
⛽ *Used:* {data.gasoline_used}
⛽ *Left:* {data.gasoline_left}

🛣 *Mileage:* {data.mileage_ride if data.mileage_ride else '—'}
📷 *Photos:* {'✅' if data.mileage_photo_id or data.bill_photo_id else '—'}
"""


# Глобальный экземпляр сервиса
report_service = ReportService()
