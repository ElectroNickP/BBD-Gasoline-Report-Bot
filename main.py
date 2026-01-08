"""
BBD Gasoline Report Bot - Точка входа

Telegram бот для заполнения отчётов о топливе лодок
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config.settings import settings
from database.database import init_db
from services.dictionary_service import dictionary_service
from services.user_service import user_service

from bot.handlers.start import start_command, help_command, handle_main_menu, back_to_main_menu
from bot.handlers.report import get_report_conversation_handler
from bot.handlers.history import show_history
from bot.handlers.analytics import show_analytics_menu, handle_analytics_callback, handle_export_callback
from bot.keyboards import get_main_menu_keyboard

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Инициализация после создания приложения"""
    # Инициализация базы данных
    await init_db()
    logger.info("Database initialized")
    
    # Загрузка справочников
    dictionary_service.load()
    logger.info(f"Captains loaded: {len(dictionary_service.captains)}")
    logger.info(f"Boats loaded: {len(dictionary_service.boats)}")
    logger.info(f"Programs loaded: {len(dictionary_service.programs)}")
    logger.info(f"Piers loaded: {len(dictionary_service.piers)}")
    
    # Загрузка пользователей
    user_service.load()
    logger.info(f"Users loaded: {len(user_service.get_all_users())}")


def main():
    """Запуск бота"""
    # Проверка токена
    if not settings.bot_token:
        logger.error("BOT_TOKEN не задан! Укажите его в .env файле или переменных окружения.")
        return
    
    # Создание приложения
    application = (
        Application.builder()
        .token(settings.bot_token)
        .post_init(post_init)
        .build()
    )
    
    # Регистрация обработчиков
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # ConversationHandler для отчёта
    application.add_handler(get_report_conversation_handler())
    
    # Callback handler for analytics
    application.add_handler(CallbackQueryHandler(
        handle_analytics_callback,
        pattern=r'^analytics:'
    ))
    
    # Callback handler for CSV export
    application.add_handler(CallbackQueryHandler(
        handle_export_callback,
        pattern=r'^export:'
    ))
    
    # Callback handler для возврата в главное меню
    application.add_handler(CallbackQueryHandler(
        back_to_main_menu,
        pattern=r'^main_menu$'
    ))
    
    # Main menu handlers
    application.add_handler(MessageHandler(
        filters.Regex(r'^📊 Analytics'), 
        show_analytics_menu
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^📋 History'), 
        show_history
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^ℹ️'), 
        handle_main_menu
    ))
    
    # Запуск
    logger.info("Starting BBD Gasoline Report Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
