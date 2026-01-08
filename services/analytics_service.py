"""
Analytics service for fuel reports
"""
import csv
import io
from datetime import date, timedelta
from typing import Optional
from dataclasses import dataclass

from database.repository import report_repository


@dataclass
class PeriodFilter:
    """Period filter"""
    start_date: date
    end_date: date
    
    @classmethod
    def last_week(cls) -> 'PeriodFilter':
        end = date.today()
        start = end - timedelta(days=7)
        return cls(start, end)
    
    @classmethod
    def last_month(cls) -> 'PeriodFilter':
        end = date.today()
        start = end - timedelta(days=30)
        return cls(start, end)
    
    @classmethod
    def this_month(cls) -> 'PeriodFilter':
        today = date.today()
        start = today.replace(day=1)
        return cls(start, today)
    
    @classmethod
    def last_3_months(cls) -> 'PeriodFilter':
        end = date.today()
        start = end - timedelta(days=90)
        return cls(start, end)


class AnalyticsService:
    """Analytics service"""
    
    async def get_boat_analytics(
        self,
        period: Optional[PeriodFilter] = None
    ) -> str:
        """Boat analytics"""
        start = period.start_date if period else None
        end = period.end_date if period else None
        
        stats = await report_repository.get_boat_stats(start, end)
        
        if not stats:
            return "📊 *Boat Analytics*\n\nNo data for selected period."
        
        # Sort by efficiency (less consumption = better)
        stats_sorted = sorted(stats, key=lambda x: x['avg_fuel_used'])
        
        period_text = ""
        if period:
            period_text = f"\n📅 Period: {period.start_date.strftime('%d.%m')} — {period.end_date.strftime('%d.%m.%Y')}\n"
        
        text = f"🚤 *Boat Analytics*{period_text}\n"
        
        for i, s in enumerate(stats_sorted, 1):
            # Medals for top-3
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            text += f"\n{medal}*{s['boat_name']}*\n"
            text += f"   📊 Trips: {s['trips_count']}\n"
            text += f"   ⛽ Avg. consumption: {s['avg_fuel_used']}L\n"
            text += f"   ⚡ Avg. speed: {s['avg_speed']}\n"
            text += f"   🔋 Total consumed: {s['total_fuel_used']}L\n"
        
        return text
    
    async def get_captain_analytics(
        self,
        period: Optional[PeriodFilter] = None
    ) -> str:
        """Captain analytics"""
        start = period.start_date if period else None
        end = period.end_date if period else None
        
        stats = await report_repository.get_captain_stats(start, end)
        
        if not stats:
            return "📊 *Captain Analytics*\n\nNo data for selected period."
        
        # Sort by number of trips
        stats_sorted = sorted(stats, key=lambda x: x['trips_count'], reverse=True)
        
        period_text = ""
        if period:
            period_text = f"\n📅 Period: {period.start_date.strftime('%d.%m')} — {period.end_date.strftime('%d.%m.%Y')}\n"
        
        text = f"👨‍✈️ *Captain Analytics*{period_text}\n"
        
        for i, s in enumerate(stats_sorted, 1):
            medal = ""
            if i == 1:
                medal = "🏆 "
            
            text += f"\n{medal}*{s['captain_name']}*\n"
            text += f"   📊 Trips: {s['trips_count']}\n"
            text += f"   ⛽ Avg. consumption: {s['avg_fuel_used']}L\n"
            text += f"   ⚡ Avg. speed: {s['avg_speed']}\n"
            text += f"   🔋 Total consumed: {s['total_fuel_used']}L\n"
            text += f"   ⛽ Total refueled: {s['total_refuel']}L\n"
        
        return text
    
    async def get_program_analytics(
        self,
        period: Optional[PeriodFilter] = None
    ) -> str:
        """Program/route analytics"""
        start = period.start_date if period else None
        end = period.end_date if period else None
        
        stats = await report_repository.get_program_stats(start, end)
        
        if not stats:
            return "📊 *Program Analytics*\n\nNo data for selected period."
        
        # Sort by average consumption
        stats_sorted = sorted(stats, key=lambda x: x['avg_fuel_used'], reverse=True)
        
        period_text = ""
        if period:
            period_text = f"\n📅 Period: {period.start_date.strftime('%d.%m')} — {period.end_date.strftime('%d.%m.%Y')}\n"
        
        text = f"🏝 *Consumption by Program*{period_text}\n"
        
        for s in stats_sorted:
            text += f"\n*{s['program_name']}*\n"
            text += f"   📊 Trips: {s['trips_count']}\n"
            text += f"   ⛽ Avg. consumption: {s['avg_fuel_used']}L\n"
            text += f"   🔋 Total: {s['total_fuel_used']}L\n"
        
        return text
    
    async def get_period_summary(
        self,
        period: PeriodFilter
    ) -> str:
        """Period summary"""
        summary = await report_repository.get_period_summary(
            period.start_date, 
            period.end_date
        )
        
        period_text = f"{period.start_date.strftime('%d.%m')} — {period.end_date.strftime('%d.%m.%Y')}"
        
        if summary['total_trips'] == 0:
            return f"📊 *Period Summary*\n📅 {period_text}\n\nNo data for selected period."
        
        text = f"""📊 *Period Summary*
📅 {period_text}

📈 *General Statistics:*
   🚤 Total trips: {summary['total_trips']}
   ⛽ Fuel consumed: {summary['total_fuel_used']}L
   🔋 Fuel refueled: {summary['total_refuel']}L
   📊 Avg. consumption per trip: {summary['avg_fuel_per_trip']}L
   ⚡ Avg. max speed: {summary['avg_speed']}
"""
        return text
    
    async def get_recent_reports(
        self,
        period: PeriodFilter,
        limit: int = 10
    ) -> str:
        """Recent reports for period"""
        reports = await report_repository.get_by_date_range(
            period.start_date,
            period.end_date
        )
        
        if not reports:
            return "📋 *Reports*\n\nNo reports for selected period."
        
        reports = reports[:limit]
        
        period_text = f"{period.start_date.strftime('%d.%m')} — {period.end_date.strftime('%d.%m.%Y')}"
        text = f"📋 *Reports for Period*\n📅 {period_text}\n\n"
        
        for r in reports:
            program = r.program_name
            if r.private_program:
                program = f"{program} → {r.private_program}"
            
            text += f"*{r.departure_date.strftime('%d.%m')}* | {r.captain_name} | {r.boat_name}\n"
            text += f"   🏝 {program}\n"
            text += f"   ⛽ Used: {r.gasoline_used}L | Refueled: {r.gasoline_refuel}L\n\n"
        
        if len(reports) < len(await report_repository.get_by_date_range(period.start_date, period.end_date)):
            text += f"_...showing {limit} of {len(await report_repository.get_by_date_range(period.start_date, period.end_date))} reports_"
        
        return text
    
    async def get_efficiency_ranking(
        self,
        period: Optional[PeriodFilter] = None
    ) -> str:
        """Efficiency ranking (captain + boat)"""
        start = period.start_date if period else None
        end = period.end_date if period else None
        
        boat_stats = await report_repository.get_boat_stats(start, end)
        captain_stats = await report_repository.get_captain_stats(start, end)
        
        if not boat_stats and not captain_stats:
            return "📊 *Efficiency Ranking*\n\nNo data."
        
        period_text = ""
        if period:
            period_text = f"\n📅 {period.start_date.strftime('%d.%m')} — {period.end_date.strftime('%d.%m.%Y')}\n"
        
        text = f"🏆 *Efficiency Ranking*{period_text}\n"
        
        # Top boats by fuel efficiency
        if boat_stats:
            boats_sorted = sorted(boat_stats, key=lambda x: x['avg_fuel_used'])[:3]
            text += "\n🚤 *Most Efficient Boats:*\n"
            for i, b in enumerate(boats_sorted, 1):
                medals = ["🥇", "🥈", "🥉"]
                text += f"{medals[i-1]} {b['boat_name']} — {b['avg_fuel_used']}L/trip\n"
        
        # Top captains by trips count
        if captain_stats:
            captains_sorted = sorted(captain_stats, key=lambda x: x['trips_count'], reverse=True)[:3]
            text += "\n👨‍✈️ *Most Active Captains:*\n"
            for i, c in enumerate(captains_sorted, 1):
                medals = ["🥇", "🥈", "🥉"]
                text += f"{medals[i-1]} {c['captain_name']} — {c['trips_count']} trips\n"
        
        # Top captains by efficiency (min 3 trips)
        if captain_stats:
            captains_eco = [c for c in captain_stats if c['trips_count'] >= 3]
            if captains_eco:
                captains_eco_sorted = sorted(captains_eco, key=lambda x: x['avg_fuel_used'])[:3]
                text += "\n⛽ *Most Efficient Captains:*\n"
                text += "_(minimum 3 trips)_\n"
                for i, c in enumerate(captains_eco_sorted, 1):
                    medals = ["🥇", "🥈", "🥉"]
                    text += f"{medals[i-1]} {c['captain_name']} — {c['avg_fuel_used']}L/trip\n"
        
        return text
    
    async def export_reports_csv(
        self,
        period: Optional[PeriodFilter] = None
    ) -> io.BytesIO:
        """Export reports to CSV format for Google Sheets"""
        if period:
            reports = await report_repository.get_by_date_range(
                period.start_date,
                period.end_date
            )
        else:
            reports = await report_repository.get_all_reports()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            'Date',
            'Captain',
            'Boat',
            'Program',
            'Private Tour',
            'Pier',
            'Departure',
            'Return',
            'Refill Date',
            'Max Speed',
            'Refueled (L)',
            'Total Fuel (L)',
            'Used (L)',
            'Remaining (L)',
            'Mileage'
        ])
        
        # Data rows
        for r in reports:
            writer.writerow([
                r.departure_date.strftime('%d.%m.%Y'),
                r.captain_name,
                r.boat_name,
                r.program_name,
                r.private_program or '',
                r.departure_pier,
                r.departure_date.strftime('%d.%m.%Y'),
                r.return_date.strftime('%d.%m.%Y'),
                r.refill_date.strftime('%d.%m.%Y'),
                r.max_speed,
                r.gasoline_refuel,
                r.total_gasoline,
                r.gasoline_used,
                r.gasoline_left,
                r.mileage_ride or ''
            ])
        
        # Convert to bytes for Telegram
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))  # BOM for Excel
        bytes_output.name = f'fuel_reports_{date.today().strftime("%Y%m%d")}.csv'
        
        return bytes_output
    
    async def export_boat_stats_csv(
        self,
        period: Optional[PeriodFilter] = None
    ) -> io.BytesIO:
        """Export boat statistics to CSV"""
        start = period.start_date if period else None
        end = period.end_date if period else None
        
        stats = await report_repository.get_boat_stats(start, end)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Boat',
            'Trips',
            'Avg Consumption (L)',
            'Total Consumed (L)',
            'Avg Speed',
            'Avg Refuel (L)',
            'Total Refueled (L)'
        ])
        
        for s in stats:
            writer.writerow([
                s['boat_name'],
                s['trips_count'],
                s['avg_fuel_used'],
                s['total_fuel_used'],
                s['avg_speed'],
                s['avg_refuel'],
                s['total_refuel']
            ])
        
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
        bytes_output.name = f'boat_stats_{date.today().strftime("%Y%m%d")}.csv'
        
        return bytes_output
    
    async def export_captain_stats_csv(
        self,
        period: Optional[PeriodFilter] = None
    ) -> io.BytesIO:
        """Export captain statistics to CSV"""
        start = period.start_date if period else None
        end = period.end_date if period else None
        
        stats = await report_repository.get_captain_stats(start, end)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Captain',
            'Trips',
            'Avg Consumption (L)',
            'Total Consumed (L)',
            'Avg Speed',
            'Avg Refuel (L)',
            'Total Refueled (L)'
        ])
        
        for s in stats:
            writer.writerow([
                s['captain_name'],
                s['trips_count'],
                s['avg_fuel_used'],
                s['total_fuel_used'],
                s['avg_speed'],
                s['avg_refuel'],
                s['total_refuel']
            ])
        
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
        bytes_output.name = f'captain_stats_{date.today().strftime("%Y%m%d")}.csv'
        
        return bytes_output


# Global service instance
analytics_service = AnalyticsService()
