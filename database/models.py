"""
SQLAlchemy модели базы данных
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для моделей"""
    pass


class Report(Base):
    """Модель отчёта о топливе"""
    
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Основные данные
    captain_name: Mapped[str] = mapped_column(String(100), nullable=False)
    boat_name: Mapped[str] = mapped_column(String(100), nullable=False)
    program_name: Mapped[str] = mapped_column(String(100), nullable=False)
    private_program: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Маршрут приватного тура
    departure_pier: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Даты
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    refill_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Данные о топливе
    max_speed: Mapped[int] = mapped_column(Integer, nullable=False)
    gasoline_refuel: Mapped[float] = mapped_column(Float, nullable=False)
    total_gasoline: Mapped[float] = mapped_column(Float, nullable=False)
    gasoline_used: Mapped[float] = mapped_column(Float, nullable=False)
    gasoline_left: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Опциональные поля
    mileage_ride: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_photo_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    bill_photo_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    
    def __repr__(self) -> str:
        return (
            f"Report(id={self.id}, captain={self.captain_name}, "
            f"boat={self.boat_name}, date={self.departure_date})"
        )
