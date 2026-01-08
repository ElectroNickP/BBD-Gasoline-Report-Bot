"""
Handlers for /start and /help commands
"""
from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import get_main_menu_keyboard
from services.user_service import user_service


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command"""
    user = update.effective_user
    
    # Access check
    if not user_service.is_allowed(user.id):
        await update.message.reply_text(
            "⛔ You don't have access to this bot.\n"
            "Contact the administrator."
        )
        return
    
    # Reset session data
    context.user_data.clear()
    
    await update.message.reply_text(
        f"👋 Hello, {user.first_name}!\n\n"
        "🚤 *BBD Gasoline Report Bot*\n\n"
        "This bot helps you fill out fuel reports.\n\n"
        "Choose an action:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command"""
    help_text = """
ℹ️ *BBD Gasoline Report Bot*

*Commands:*
/start - Start the bot
/help - Show help
/cancel - Cancel current action

*How to fill a report:*
1. Press "📝 New Report"
2. Select captain, boat, program and pier
3. Enter dates
4. Enter fuel data
5. Optionally add photos
6. Confirm submission

*Navigation:*
• ⬅️ Back - return to previous step
• ❌ Cancel - cancel filling
• ⏭ Skip - skip optional field
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for help button from main menu"""
    await help_command(update, context)


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback handler to return to main menu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🏠 *Main Menu*\n\n"
        "Choose an action using the buttons below:",
        parse_mode='Markdown'
    )
    
    await query.message.reply_text(
        "Choose an action:",
        reply_markup=get_main_menu_keyboard()
    )
