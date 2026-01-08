"""
Handlers for analytics and reports viewing
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.analytics_service import analytics_service, PeriodFilter


def get_analytics_menu_keyboard() -> InlineKeyboardMarkup:
    """Analytics main menu"""
    keyboard = [
        [InlineKeyboardButton("🚤 By Boats", callback_data="analytics:boats")],
        [InlineKeyboardButton("👨‍✈️ By Captains", callback_data="analytics:captains")],
        [InlineKeyboardButton("🏝 By Programs", callback_data="analytics:programs")],
        [InlineKeyboardButton("🏆 Efficiency Ranking", callback_data="analytics:ranking")],
        [InlineKeyboardButton("📋 Reports by Period", callback_data="analytics:reports")],
        [InlineKeyboardButton("📊 Period Summary", callback_data="analytics:summary")],
        [InlineKeyboardButton("📥 Export to CSV", callback_data="analytics:export")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_period_keyboard(callback_prefix: str) -> InlineKeyboardMarkup:
    """Period selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("7 days", callback_data=f"{callback_prefix}:week"),
            InlineKeyboardButton("30 days", callback_data=f"{callback_prefix}:month")
        ],
        [
            InlineKeyboardButton("This month", callback_data=f"{callback_prefix}:this_month"),
            InlineKeyboardButton("3 months", callback_data=f"{callback_prefix}:3months")
        ],
        [InlineKeyboardButton("All time", callback_data=f"{callback_prefix}:all")],
        [InlineKeyboardButton("⬅️ Back", callback_data="analytics:menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_analytics_keyboard() -> InlineKeyboardMarkup:
    """Back to analytics menu button"""
    keyboard = [
        [InlineKeyboardButton("⬅️ Analytics Menu", callback_data="analytics:menu")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_export_keyboard() -> InlineKeyboardMarkup:
    """Export type selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 All Reports", callback_data="export:reports")],
        [InlineKeyboardButton("🚤 Boat Statistics", callback_data="export:boats")],
        [InlineKeyboardButton("👨‍✈️ Captain Statistics", callback_data="export:captains")],
        [InlineKeyboardButton("⬅️ Back", callback_data="analytics:menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_period_from_callback(period_code: str) -> PeriodFilter | None:
    """Get period filter from callback code"""
    if period_code == "week":
        return PeriodFilter.last_week()
    elif period_code == "month":
        return PeriodFilter.last_month()
    elif period_code == "this_month":
        return PeriodFilter.this_month()
    elif period_code == "3months":
        return PeriodFilter.last_3_months()
    elif period_code == "all":
        return None
    return None


async def show_analytics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show analytics menu"""
    text = "📊 *Analytics & Reports*\n\nSelect analytics type:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text,
            reply_markup=get_analytics_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=get_analytics_menu_keyboard(),
            parse_mode='Markdown'
        )


async def handle_analytics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle analytics callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    action = data[1] if len(data) > 1 else ""
    period_code = data[2] if len(data) > 2 else None
    
    if action == "menu":
        await show_analytics_menu(update, context)
        return
    
    # Export menu
    if action == "export":
        await query.edit_message_text(
            "📥 *Export to CSV*\n\n"
            "Select what to export:\n"
            "_(Files can be imported to Google Sheets)_",
            reply_markup=get_export_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # If period selection needed
    if action in ["boats", "captains", "programs", "ranking", "reports", "summary"] and not period_code:
        await query.edit_message_text(
            f"📅 *Select period:*",
            reply_markup=get_period_keyboard(f"analytics:{action}"),
            parse_mode='Markdown'
        )
        return
    
    # Get period
    period = get_period_from_callback(period_code) if period_code else None
    
    # Process different analytics types
    if action == "boats":
        text = await analytics_service.get_boat_analytics(period)
    elif action == "captains":
        text = await analytics_service.get_captain_analytics(period)
    elif action == "programs":
        text = await analytics_service.get_program_analytics(period)
    elif action == "ranking":
        text = await analytics_service.get_efficiency_ranking(period)
    elif action == "reports":
        if period:
            text = await analytics_service.get_recent_reports(period)
        else:
            text = await analytics_service.get_recent_reports(PeriodFilter.last_3_months())
    elif action == "summary":
        if period:
            text = await analytics_service.get_period_summary(period)
        else:
            text = await analytics_service.get_period_summary(PeriodFilter.last_3_months())
    else:
        text = "Unknown action"
    
    await query.edit_message_text(
        text,
        reply_markup=get_back_to_analytics_keyboard(),
        parse_mode='Markdown'
    )


async def handle_export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle export callbacks - send CSV files"""
    query = update.callback_query
    await query.answer("Generating file...")
    
    data = query.data.split(":")
    export_type = data[1] if len(data) > 1 else ""
    
    try:
        if export_type == "reports":
            csv_file = await analytics_service.export_reports_csv()
            caption = "📋 All fuel reports"
        elif export_type == "boats":
            csv_file = await analytics_service.export_boat_stats_csv()
            caption = "🚤 Boat statistics"
        elif export_type == "captains":
            csv_file = await analytics_service.export_captain_stats_csv()
            caption = "👨‍✈️ Captain statistics"
        else:
            await query.edit_message_text("Unknown export type")
            return
        
        await query.message.reply_document(
            document=csv_file,
            caption=f"{caption}\n\n_Import to Google Sheets: File → Import → Upload_",
            parse_mode='Markdown'
        )
        
        await query.edit_message_text(
            "✅ File sent!\n\n"
            "To import to Google Sheets:\n"
            "1. Open Google Sheets\n"
            "2. File → Import\n"
            "3. Upload the CSV file\n"
            "4. Select 'Replace spreadsheet' or 'Insert new sheet'",
            reply_markup=get_back_to_analytics_keyboard()
        )
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Export error: {str(e)}",
            reply_markup=get_back_to_analytics_keyboard()
        )
