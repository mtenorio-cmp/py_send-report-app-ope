import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from services.authorization_store_memory import InMemoryAuthorizationStore
from services.telegram_handlers import BotHandlers

logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self, token: str, admin_id: int, auth_store=None):
        self.token = token
        self.admin_id = admin_id
        self.auth_store = auth_store or InMemoryAuthorizationStore()
        self.handlers = BotHandlers(admin_id, self.auth_store)

    async def run(self):
        app = Application.builder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.handlers.start))
        app.add_handler(CallbackQueryHandler(self.handlers.button))

        await app.initialize()
        await app.start()
        logger.info("🤖 Bot de Telegram iniciado...")

        await app.updater.start_polling()
        await asyncio.Event().wait()
