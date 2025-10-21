import asyncio
import logging
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from interfaces.database_interface import IDatabaseConnection
from interfaces.telegram_authorization_store import ITelegramAuthorizationStore
from services.telegram_handlers import BotHandlers

logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self, token: str, admin_id: int, auth_store: ITelegramAuthorizationStore, db_connection: IDatabaseConnection):
        self.token = token
        self.admin_id = admin_id
        self.auth_store =  auth_store

        self.handlers = BotHandlers(
            admin_id=admin_id, 
            auth_store=self.auth_store, 
            db_connection=db_connection
        )

    async def run(self):
        app = Application.builder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.handlers.start))
        app.add_handler(CommandHandler("ruta_programada_hoy", self.handlers.ruta_programada_hoy))
        app.add_handler(CallbackQueryHandler(self.handlers.button))

        # Registrar lista de comandos para autocompletado
        commands = [
            BotCommand("start", "Inicia el bot y te registra"),
            BotCommand("ruta_programada_hoy", "Obtén la ruta programada para hoy"),
        ]
        await app.bot.set_my_commands(commands)

        await app.initialize()
        await app.start()
        logger.info("🤖 Bot de Telegram iniciado...")

        await app.updater.start_polling()
        await asyncio.Event().wait()
