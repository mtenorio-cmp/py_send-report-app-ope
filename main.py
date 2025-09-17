from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from database.mariadb_connection import MariaDBConnection
from routes import guia_route, promedio_tiempo_despacho_x_cond_pago
from config import settings  
from stores.telegram_authorization_sql_store import TelegramAuthorizationSqlStore
from services.telegram_bot_service import TelegramBotService
import asyncio
from contextlib import asynccontextmanager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

db = MariaDBConnection()

# Iniciar el bot de Telegram
auth_store = TelegramAuthorizationSqlStore(db)

telegram_service = TelegramBotService(
    token=settings.TELEGRAM_BOT_TOKEN,
    admin_id=int(settings.TELEGRAM_ADMIN_ID),
    auth_store=auth_store,
    db_connection=db
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 Startup
    bot_task = asyncio.create_task(telegram_service.run())
    
    logger.info("Bot de Telegram iniciado junto con la API")
    yield
    # 🛑 Shutdown
    bot_task.cancel()
    logger.warning("Bot detenido porque la API se cerró")

# Inicialización de la aplicación
app = FastAPI(
    title="API de Análisis de Datos",
    description="API para consultas y análisis de datos en MariaDB",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(promedio_tiempo_despacho_x_cond_pago.router)
app.include_router(guia_route.router)

# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "API de Análisis de Datos",
        "version": "1.0.0",
        "status": "✅",
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )