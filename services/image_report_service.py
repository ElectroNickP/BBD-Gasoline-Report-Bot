"""
Service for generating report images (tables as images)
"""
import io
from datetime import date, timedelta
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass

from database.repository import report_repository
from database.models import Report


@dataclass
class TableConfig:
    """Table styling configuration"""
    # Colors
    header_bg: str = "#1a5f7a"
    header_text: str = "#ffffff"
    row_bg_even: str = "#f8f9fa"
    row_bg_odd: str = "#ffffff"
    row_text: str = "#212529"
    border_color: str = "#dee2e6"
    title_bg: str = "#0d3d4d"
    title_text: str = "#ffffff"
    summary_bg: str = "#e8f4f8"
    
    # Sizes
    cell_padding: int = 12
    row_height: int = 40
    header_height: int = 45
    title_height: int = 50
    font_size: int = 14
    header_font_size: int = 15
    title_font_size: int = 20
    border_width: int = 1


class ImageReportService:
    """Service for generating report images"""
    
    def __init__(self):
        self.config = TableConfig()
        # Try to load a good font, fallback to default
        self._font = None
        self._font_bold = None
        self._title_font = None
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with fallback"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
        
        if bold:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            ] + font_paths
        
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
        
        return ImageFont.load_default()
    
    def _calculate_column_widths(
        self, 
        headers: List[str], 
        rows: List[List[str]], 
        draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont
    ) -> List[int]:
        """Calculate optimal column widths based on content"""
        widths = []
        padding = self.config.cell_padding * 2
        
        for col_idx in range(len(headers)):
            # Start with header width
            header_width = draw.textlength(headers[col_idx], font=font) + padding
            max_width = header_width
            
            # Check all rows
            for row in rows:
                if col_idx < len(row):
                    cell_width = draw.textlength(str(row[col_idx]), font=font) + padding
                    max_width = max(max_width, cell_width)
            
            # Set min/max constraints
            widths.append(max(80, min(int(max_width), 200)))
        
        return widths
    
    def generate_table_image(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        summary_rows: Optional[List[List[str]]] = None
    ) -> io.BytesIO:
        """Generate a table image"""
        cfg = self.config
        
        # Get fonts
        font = self._get_font(cfg.font_size)
        font_bold = self._get_font(cfg.header_font_size, bold=True)
        title_font = self._get_font(cfg.title_font_size, bold=True)
        
        # Create temporary image to calculate sizes
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate column widths
        col_widths = self._calculate_column_widths(headers, rows, temp_draw, font)
        
        # Calculate total dimensions
        total_width = sum(col_widths) + cfg.border_width
        
        summary_count = len(summary_rows) if summary_rows else 0
        total_height = (
            cfg.title_height +
            cfg.header_height +
            (len(rows) * cfg.row_height) +
            (summary_count * cfg.row_height) +
            cfg.border_width * 2
        )
        
        # Create actual image
        img = Image.new('RGB', (total_width, total_height), '#ffffff')
        draw = ImageDraw.Draw(img)
        
        y = 0
        
        # Draw title
        draw.rectangle(
            [(0, y), (total_width, y + cfg.title_height)],
            fill=cfg.title_bg
        )
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = (total_width - (title_bbox[2] - title_bbox[0])) // 2
        title_y = y + (cfg.title_height - (title_bbox[3] - title_bbox[1])) // 2
        draw.text((title_x, title_y), title, fill=cfg.title_text, font=title_font)
        y += cfg.title_height
        
        # Draw header
        draw.rectangle(
            [(0, y), (total_width, y + cfg.header_height)],
            fill=cfg.header_bg
        )
        
        x = 0
        for col_idx, header in enumerate(headers):
            # Draw header text centered
            text_bbox = draw.textbbox((0, 0), header, font=font_bold)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = x + (col_widths[col_idx] - text_width) // 2
            text_y = y + (cfg.header_height - text_height) // 2
            draw.text((text_x, text_y), header, fill=cfg.header_text, font=font_bold)
            
            # Draw vertical line
            if col_idx < len(headers) - 1:
                line_x = x + col_widths[col_idx]
                draw.line([(line_x, y), (line_x, y + cfg.header_height)], 
                         fill=cfg.border_color, width=cfg.border_width)
            
            x += col_widths[col_idx]
        
        y += cfg.header_height
        
        # Draw data rows
        for row_idx, row in enumerate(rows):
            bg_color = cfg.row_bg_even if row_idx % 2 == 0 else cfg.row_bg_odd
            draw.rectangle(
                [(0, y), (total_width, y + cfg.row_height)],
                fill=bg_color
            )
            
            x = 0
            for col_idx, cell in enumerate(row):
                cell_str = str(cell) if cell else ""
                text_bbox = draw.textbbox((0, 0), cell_str, font=font)
                text_height = text_bbox[3] - text_bbox[1]
                text_y = y + (cfg.row_height - text_height) // 2
                
                # Right-align numbers, left-align text
                if col_idx > 0 and cell_str.replace('.', '').replace('-', '').isdigit():
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = x + col_widths[col_idx] - text_width - cfg.cell_padding
                else:
                    text_x = x + cfg.cell_padding
                
                draw.text((text_x, text_y), cell_str, fill=cfg.row_text, font=font)
                
                # Draw vertical line
                if col_idx < len(row) - 1:
                    line_x = x + col_widths[col_idx]
                    draw.line([(line_x, y), (line_x, y + cfg.row_height)], 
                             fill=cfg.border_color, width=cfg.border_width)
                
                x += col_widths[col_idx]
            
            # Draw horizontal line
            draw.line([(0, y + cfg.row_height), (total_width, y + cfg.row_height)], 
                     fill=cfg.border_color, width=cfg.border_width)
            
            y += cfg.row_height
        
        # Draw summary rows if provided
        if summary_rows:
            for summary_row in summary_rows:
                draw.rectangle(
                    [(0, y), (total_width, y + cfg.row_height)],
                    fill=cfg.summary_bg
                )
                
                x = 0
                for col_idx, cell in enumerate(summary_row):
                    cell_str = str(cell) if cell else ""
                    text_bbox = draw.textbbox((0, 0), cell_str, font=font_bold)
                    text_height = text_bbox[3] - text_bbox[1]
                    text_y = y + (cfg.row_height - text_height) // 2
                    
                    if col_idx > 0 and cell_str.replace('.', '').replace('-', '').isdigit():
                        text_width = text_bbox[2] - text_bbox[0]
                        text_x = x + col_widths[col_idx] - text_width - cfg.cell_padding
                    else:
                        text_x = x + cfg.cell_padding
                    
                    draw.text((text_x, text_y), cell_str, fill=cfg.row_text, font=font_bold)
                    
                    if col_idx < len(summary_row) - 1:
                        line_x = x + col_widths[col_idx]
                        draw.line([(line_x, y), (line_x, y + cfg.row_height)], 
                                 fill=cfg.border_color, width=cfg.border_width)
                    
                    x += col_widths[col_idx]
                
                y += cfg.row_height
        
        # Draw border
        draw.rectangle(
            [(0, 0), (total_width - 1, total_height - 1)],
            outline=cfg.border_color,
            width=2
        )
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True)
        output.seek(0)
        output.name = 'report.png'
        
        return output
    
    async def generate_daily_report(
        self,
        report_date: Optional[date] = None
    ) -> io.BytesIO:
        """Generate daily report image"""
        if report_date is None:
            report_date = date.today()
        
        reports = await report_repository.get_by_date_range(report_date, report_date)
        
        title = f"Daily Report - {report_date.strftime('%d.%m.%Y')}"
        
        headers = ["Captain", "Boat", "Program", "Refuel", "Used", "Left", "Speed"]
        
        rows = []
        total_refuel = 0
        total_used = 0
        
        for r in reports:
            program = r.program_name
            if r.private_program:
                program = f"N/A→{r.private_program[:8]}"
            
            rows.append([
                r.captain_name,
                r.boat_name,
                program[:12],
                f"{r.gasoline_refuel:.0f}",
                f"{r.gasoline_used:.0f}",
                f"{r.gasoline_left:.0f}",
                str(r.max_speed)
            ])
            total_refuel += r.gasoline_refuel
            total_used += r.gasoline_used
        
        if not rows:
            rows.append(["No reports", "-", "-", "-", "-", "-", "-"])
            summary = None
        else:
            summary = [["TOTAL", f"{len(rows)} trips", "", f"{total_refuel:.0f}", f"{total_used:.0f}", "", ""]]
        
        return self.generate_table_image(title, headers, rows, summary)
    
    async def generate_period_report(
        self,
        start_date: date,
        end_date: date,
        title_prefix: str = "Report"
    ) -> io.BytesIO:
        """Generate period report image"""
        reports = await report_repository.get_by_date_range(start_date, end_date)
        
        if start_date == end_date:
            title = f"{title_prefix} - {start_date.strftime('%d.%m.%Y')}"
        else:
            title = f"{title_prefix} - {start_date.strftime('%d.%m')} to {end_date.strftime('%d.%m.%Y')}"
        
        headers = ["Date", "Captain", "Boat", "Program", "Refuel", "Used", "Speed"]
        
        rows = []
        total_refuel = 0
        total_used = 0
        
        for r in reports:
            program = r.program_name
            if r.private_program:
                program = f"N/A→{r.private_program[:6]}"
            
            rows.append([
                r.departure_date.strftime('%d.%m'),
                r.captain_name,
                r.boat_name[:8],
                program[:10],
                f"{r.gasoline_refuel:.0f}",
                f"{r.gasoline_used:.0f}",
                str(r.max_speed)
            ])
            total_refuel += r.gasoline_refuel
            total_used += r.gasoline_used
        
        if not rows:
            rows.append(["No data", "-", "-", "-", "-", "-", "-"])
            summary = None
        else:
            summary = [["TOTAL", f"{len(rows)} trips", "", "", f"{total_refuel:.0f}", f"{total_used:.0f}", ""]]
        
        return self.generate_table_image(title, headers, rows, summary)
    
    async def generate_boat_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> io.BytesIO:
        """Generate boat summary image"""
        stats = await report_repository.get_boat_stats(start_date, end_date)
        
        if start_date and end_date:
            title = f"Boat Summary - {start_date.strftime('%d.%m')} to {end_date.strftime('%d.%m.%Y')}"
        else:
            title = "Boat Summary - All Time"
        
        headers = ["Boat", "Trips", "Avg Used", "Total Used", "Avg Speed"]
        
        rows = []
        total_trips = 0
        total_fuel = 0
        
        # Sort by efficiency (avg fuel used)
        stats_sorted = sorted(stats, key=lambda x: x['avg_fuel_used'])
        
        for s in stats_sorted:
            rows.append([
                s['boat_name'],
                str(s['trips_count']),
                f"{s['avg_fuel_used']:.1f}",
                f"{s['total_fuel_used']:.0f}",
                f"{s['avg_speed']:.0f}"
            ])
            total_trips += s['trips_count']
            total_fuel += s['total_fuel_used']
        
        if not rows:
            rows.append(["No data", "-", "-", "-", "-"])
            summary = None
        else:
            summary = [["TOTAL", str(total_trips), "", f"{total_fuel:.0f}", ""]]
        
        return self.generate_table_image(title, headers, rows, summary)
    
    async def generate_captain_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> io.BytesIO:
        """Generate captain summary image"""
        stats = await report_repository.get_captain_stats(start_date, end_date)
        
        if start_date and end_date:
            title = f"Captain Summary - {start_date.strftime('%d.%m')} to {end_date.strftime('%d.%m.%Y')}"
        else:
            title = "Captain Summary - All Time"
        
        headers = ["Captain", "Trips", "Avg Used", "Total Used", "Avg Speed"]
        
        rows = []
        total_trips = 0
        total_fuel = 0
        
        # Sort by trips count
        stats_sorted = sorted(stats, key=lambda x: x['trips_count'], reverse=True)
        
        for s in stats_sorted:
            rows.append([
                s['captain_name'],
                str(s['trips_count']),
                f"{s['avg_fuel_used']:.1f}",
                f"{s['total_fuel_used']:.0f}",
                f"{s['avg_speed']:.0f}"
            ])
            total_trips += s['trips_count']
            total_fuel += s['total_fuel_used']
        
        if not rows:
            rows.append(["No data", "-", "-", "-", "-"])
            summary = None
        else:
            summary = [["TOTAL", str(total_trips), "", f"{total_fuel:.0f}", ""]]
        
        return self.generate_table_image(title, headers, rows, summary)
    
    async def generate_weekly_report(self) -> io.BytesIO:
        """Generate weekly report image (last 7 days)"""
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        return await self.generate_period_report(
            start_date, 
            end_date, 
            "Weekly Report"
        )
    
    async def generate_monthly_report(self) -> io.BytesIO:
        """Generate monthly report image (current month)"""
        today = date.today()
        start_date = today.replace(day=1)
        end_date = today
        
        return await self.generate_period_report(
            start_date, 
            end_date, 
            f"Monthly Report - {today.strftime('%B %Y')}"
        )


# Global service instance
image_report_service = ImageReportService()
