import logging
import asyncio
from database.mariadb_connection import MariaDBConnection
from config import settings 
from stores.telegram_authorization_sql_store import TelegramAuthorizationSqlStore
from services.telegram_bot_service import TelegramBotService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def run_bot():
    logger.info("Iniciando Bot de Telegram en modo polling...")
    db = MariaDBConnection()
    auth_store = TelegramAuthorizationSqlStore(db)

    telegram_service = TelegramBotService(
        token=settings.TELEGRAM_BOT_TOKEN,
        admin_id=int(settings.TELEGRAM_ADMIN_ID),
        auth_store=auth_store,
        db_connection=db
    )
    
    logger.info("Iniciando Bot de Telegram en modo polling...")
    await telegram_service.run()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.warning("Bot de Telegram detenido.")