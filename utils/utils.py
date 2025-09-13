# filepath: utils/utils.py
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "access_token"
API_KEY = "os.getenv(API_KEY)"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def validate_request_auth(api_key: str = Depends(api_key_header)):
    # if api_key != API_KEY:
    #     raise HTTPException(status_code=401, detail="Invalid API Key")
    return True
    

# Placeholder para los servicios (si no dependen de la inicialización de la app)
def get_query_service():
    # Aquí iría la lógica para obtener el servicio de query
    return None

