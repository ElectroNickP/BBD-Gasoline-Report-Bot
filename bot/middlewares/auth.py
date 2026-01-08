"""
Middleware для авторизации пользователей по whitelist
"""
import logging
from telegram import Update
from telegram.ext import BaseHandler
from typing import Callable, Coroutine, Any

from services.user_service import user_service

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Middleware для проверки доступа пользователя"""
    
    def __init__(self):
        self.user_service = user_service
    
    async def check_access(self, update: Update) -> bool:
        """Проверить доступ пользователя"""
        if not update.effective_user:
            return False
        
        user_id = update.effective_user.id
        is_allowed = self.user_service.is_allowed(user_id)
        
        if not is_allowed:
            logger.warning(
                f"Access denied for user {user_id} "
                f"({update.effective_user.username})"
            )
        
        return is_allowed
    
    async def __call__(
        self, 
        update: Update, 
        handler: Callable[[Update], Coroutine[Any, Any, None]]
    ) -> None:
        """Обработка middleware"""
        if not await self.check_access(update):
            if update.message:
                await update.message.reply_text(
                    "⛔ You don't have access to this bot.\n"
                    "Contact the administrator."
                )
            return
        
        await handler(update)


# Экземпляр middleware
auth_middleware = AuthMiddleware()
