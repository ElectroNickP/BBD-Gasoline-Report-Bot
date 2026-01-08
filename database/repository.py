"""
Репозиторий для работы с отчётами
"""
from datetime import date, timedelta
from typing import Optional
from sqlalchemy import select, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Report
from .database import async_session


class ReportRepository:
    """Репозиторий для CRUD операций с отчётами"""
    
    async def create(self, report_data: dict) -> Report:
        """Создать новый отчёт"""
        async with async_session() as session:
            report = Report(**report_data)
            session.add(report)
            await session.commit()
            await session.refresh(report)
            return report
    
    async def get_by_id(self, report_id: int) -> Optional[Report]:
        """Получить отчёт по ID"""
        async with async_session() as session:
            result = await session.execute(
                select(Report).where(Report.id == report_id)
            )
            return result.scalar_one_or_none()
    
    async def get_by_user(
        self, 
        telegram_user_id: int, 
        limit: int = 10
    ) -> list[Report]:
        """Получить отчёты пользователя"""
        async with async_session() as session:
            result = await session.execute(
                select(Report)
                .where(Report.telegram_user_id == telegram_user_id)
                .order_by(desc(Report.created_at))
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def get_by_captain(
        self, 
        captain_name: str, 
        limit: int = 10
    ) -> list[Report]:
        """Получить отчёты капитана"""
        async with async_session() as session:
            result = await session.execute(
                select(Report)
                .where(Report.captain_name == captain_name)
                .order_by(desc(Report.created_at))
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> list[Report]:
        """Получить отчёты за период"""
        async with async_session() as session:
            result = await session.execute(
                select(Report)
                .where(Report.departure_date >= start_date)
                .where(Report.departure_date <= end_date)
                .order_by(desc(Report.departure_date))
            )
            return list(result.scalars().all())
    
    async def get_last_report_by_user(
        self, 
        telegram_user_id: int
    ) -> Optional[Report]:
        """Получить последний отчёт пользователя"""
        async with async_session() as session:
            result = await session.execute(
                select(Report)
                .where(Report.telegram_user_id == telegram_user_id)
                .order_by(desc(Report.created_at))
                .limit(1)
            )
            return result.scalar_one_or_none()
    
    async def delete(self, report_id: int) -> bool:
        """Удалить отчёт"""
        async with async_session() as session:
            report = await session.get(Report, report_id)
            if report:
                await session.delete(report)
                await session.commit()
                return True
            return False
    
    # ============== МЕТОДЫ АНАЛИТИКИ ==============
    
    async def get_all_reports(self, limit: int = 1000) -> list[Report]:
        """Получить все отчёты"""
        async with async_session() as session:
            result = await session.execute(
                select(Report)
                .order_by(desc(Report.departure_date))
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def get_reports_by_boat(
        self, 
        boat_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[Report]:
        """Получить отчёты по лодке за период"""
        async with async_session() as session:
            query = select(Report).where(Report.boat_name == boat_name)
            
            if start_date:
                query = query.where(Report.departure_date >= start_date)
            if end_date:
                query = query.where(Report.departure_date <= end_date)
            
            result = await session.execute(
                query.order_by(desc(Report.departure_date))
            )
            return list(result.scalars().all())
    
    async def get_reports_by_captain_period(
        self,
        captain_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[Report]:
        """Получить отчёты капитана за период"""
        async with async_session() as session:
            query = select(Report).where(Report.captain_name == captain_name)
            
            if start_date:
                query = query.where(Report.departure_date >= start_date)
            if end_date:
                query = query.where(Report.departure_date <= end_date)
            
            result = await session.execute(
                query.order_by(desc(Report.departure_date))
            )
            return list(result.scalars().all())
    
    async def get_boat_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[dict]:
        """Статистика по лодкам: расход, скорость, рейсы"""
        async with async_session() as session:
            query = select(
                Report.boat_name,
                func.count(Report.id).label('trips_count'),
                func.avg(Report.gasoline_used).label('avg_fuel_used'),
                func.sum(Report.gasoline_used).label('total_fuel_used'),
                func.avg(Report.max_speed).label('avg_speed'),
                func.avg(Report.gasoline_refuel).label('avg_refuel'),
                func.sum(Report.gasoline_refuel).label('total_refuel')
            ).group_by(Report.boat_name)
            
            if start_date:
                query = query.where(Report.departure_date >= start_date)
            if end_date:
                query = query.where(Report.departure_date <= end_date)
            
            result = await session.execute(query)
            rows = result.all()
            
            return [
                {
                    'boat_name': row.boat_name,
                    'trips_count': row.trips_count,
                    'avg_fuel_used': round(row.avg_fuel_used or 0, 1),
                    'total_fuel_used': round(row.total_fuel_used or 0, 1),
                    'avg_speed': round(row.avg_speed or 0, 1),
                    'avg_refuel': round(row.avg_refuel or 0, 1),
                    'total_refuel': round(row.total_refuel or 0, 1)
                }
                for row in rows
            ]
    
    async def get_captain_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[dict]:
        """Статистика по капитанам: расход, заправки, рейсы"""
        async with async_session() as session:
            query = select(
                Report.captain_name,
                func.count(Report.id).label('trips_count'),
                func.avg(Report.gasoline_used).label('avg_fuel_used'),
                func.sum(Report.gasoline_used).label('total_fuel_used'),
                func.avg(Report.max_speed).label('avg_speed'),
                func.avg(Report.gasoline_refuel).label('avg_refuel'),
                func.sum(Report.gasoline_refuel).label('total_refuel')
            ).group_by(Report.captain_name)
            
            if start_date:
                query = query.where(Report.departure_date >= start_date)
            if end_date:
                query = query.where(Report.departure_date <= end_date)
            
            result = await session.execute(query)
            rows = result.all()
            
            return [
                {
                    'captain_name': row.captain_name,
                    'trips_count': row.trips_count,
                    'avg_fuel_used': round(row.avg_fuel_used or 0, 1),
                    'total_fuel_used': round(row.total_fuel_used or 0, 1),
                    'avg_speed': round(row.avg_speed or 0, 1),
                    'avg_refuel': round(row.avg_refuel or 0, 1),
                    'total_refuel': round(row.total_refuel or 0, 1)
                }
                for row in rows
            ]
    
    async def get_program_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[dict]:
        """Статистика по программам: расход топлива"""
        async with async_session() as session:
            query = select(
                Report.program_name,
                func.count(Report.id).label('trips_count'),
                func.avg(Report.gasoline_used).label('avg_fuel_used'),
                func.sum(Report.gasoline_used).label('total_fuel_used')
            ).group_by(Report.program_name)
            
            if start_date:
                query = query.where(Report.departure_date >= start_date)
            if end_date:
                query = query.where(Report.departure_date <= end_date)
            
            result = await session.execute(query)
            rows = result.all()
            
            return [
                {
                    'program_name': row.program_name,
                    'trips_count': row.trips_count,
                    'avg_fuel_used': round(row.avg_fuel_used or 0, 1),
                    'total_fuel_used': round(row.total_fuel_used or 0, 1)
                }
                for row in rows
            ]
    
    async def get_period_summary(
        self,
        start_date: date,
        end_date: date
    ) -> dict:
        """Общая сводка за период"""
        async with async_session() as session:
            result = await session.execute(
                select(
                    func.count(Report.id).label('total_trips'),
                    func.sum(Report.gasoline_used).label('total_fuel_used'),
                    func.sum(Report.gasoline_refuel).label('total_refuel'),
                    func.avg(Report.gasoline_used).label('avg_fuel_per_trip'),
                    func.avg(Report.max_speed).label('avg_speed')
                )
                .where(Report.departure_date >= start_date)
                .where(Report.departure_date <= end_date)
            )
            row = result.one()
            
            return {
                'total_trips': row.total_trips or 0,
                'total_fuel_used': round(row.total_fuel_used or 0, 1),
                'total_refuel': round(row.total_refuel or 0, 1),
                'avg_fuel_per_trip': round(row.avg_fuel_per_trip or 0, 1),
                'avg_speed': round(row.avg_speed or 0, 1)
            }


# Глобальный экземпляр репозитория
report_repository = ReportRepository()
