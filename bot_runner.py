import logging
import asyncio
from database.mariadb_connection import MariaDBConnection
from config import settings
from stores.telegram_authorization_sql_store import TelegramAuthorizationSqlStore
from services.telegram_bot_service import TelegramBotService
from views.generate_dashboard.generate_dashboard import GenerateDashboard
from services.documento_query_service import DocumentoQueryService
from services.data_analysis_service import DataAnalysisService


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_bot():
    logger.info("Iniciando Bot de Telegram en modo polling...")
    db = MariaDBConnection()
    auth_store = TelegramAuthorizationSqlStore(db)

    telegram_service = TelegramBotService(
        token=settings.TELEGRAM_BOT_TOKEN,
        admin_id=int(settings.TELEGRAM_ADMIN_ID),
        auth_store=auth_store,
        db_connection=db,
    )

    logger.info("Iniciando Bot de Telegram en modo polling...")
    await telegram_service.run()


async def test_generate_dashboard():
    db = MariaDBConnection()
    query_service = DocumentoQueryService(db)
    data_analysis_service = DataAnalysisService()
    df_response = query_service.get_delivery_documents_by_date_range(
        start_date="2025-01-01",
        end_date="2025-01-15",
    )
    promedio_tiempo_despacho = data_analysis_service.get_promedio_tiempo_despacho(
        df_response
    )
    r = GenerateDashboard()
    r.init(
        data_tiempo_promedio=promedio_tiempo_despacho,
        data_exceptions=data_analysis_service.find_exceptions(df_response),
        data_programados_del_dia=data_analysis_service.find_programados_del_dia(
            df_response, "2025-01-01"
        ),
    )


if __name__ == "__main__":
    asyncio.run(test_generate_dashboard())
    # try:
    #     asyncio.run(run_bot())
    # except KeyboardInterrupt:
    #     logger.warning("Bot de Telegram detenido.")
