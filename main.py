from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from routes import promedio_tiempo_despacho_x_cond_pago, update_gr
from config import settings  

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Inicialización de la aplicación
app = FastAPI(
    title="API de Análisis de Datos",
    description="API para consultas y análisis de datos en MariaDB",
    version="1.0.0"
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
app.include_router(update_gr.router)

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