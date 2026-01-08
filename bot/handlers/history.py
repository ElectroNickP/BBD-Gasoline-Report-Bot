"""
Handler for viewing report history
"""
from telegram import Update
from telegram.ext import ContextTypes

from services.report_service import report_service
from services.user_service import user_service


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's report history"""
    user = update.effective_user
    
    # Access check
    if not user_service.is_allowed(user.id):
        await update.message.reply_text("⛔ Access denied.")
        return
    
    reports = await report_service.get_user_reports(user.id, limit=5)
    
    if not reports:
        await update.message.reply_text(
            "📊 *Report History*\n\n"
            "You don't have any reports yet.",
            parse_mode='Markdown'
        )
        return
    
    text = "📊 *Recent Reports:*\n\n"
    
    for i, report in enumerate(reports, 1):
        text += (
            f"*{i}. {report.departure_date.strftime('%d.%m.%Y')}*\n"
            f"   👨‍✈️ {report.captain_name} | 🚤 {report.boat_name}\n"
            f"   🏝 {report.program_name}\n"
            f"   ⛽ Refueled: {report.gasoline_refuel}L\n\n"
        )
    
    await update.message.reply_text(text, parse_mode='Markdown')
