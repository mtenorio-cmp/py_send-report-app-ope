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


def kg_a_toneladas(valor):
    """
    Convierte cualquier entrada (texto o número) de kg a formato legible en toneladas o kg.
    Ejemplos:
        kg_a_toneladas("15420")     → "15 ton"
        kg_a_toneladas("50,000")    → "50 ton"
        kg_a_toneladas(8750)        → "8.75 ton"
        kg_a_toneladas(85)          → "85 kg"
    """
    # 1. Convertir a string y limpiar
    texto = str(valor).strip()

    # 2. Remover comas y espacios (soporta "15,420" o "15 420")
    texto_limpio = texto.replace(",", "").replace(" ", "")

    # 3. Si hay punto decimal (ej: "15.5" o "1,234.56")
    if "." in texto_limpio:
        # Separar parte entera y decimal
        partes = texto_limpio.split(".")
        entero = partes[0]
        decimal = partes[1] if len(partes) > 1 else "0"
        texto_limpio = entero + "." + decimal

    # 4. Convertir a float (ahora es seguro)
    try:
        kg = float(texto_limpio)
    except ValueError:
        return "Error: valor no válido"

    # 5. Convertir a toneladas
    toneladas = kg / 1000.0

    # 6. Formato inteligente
    if toneladas >= 10:
        return f"{toneladas:,.0f} ton".replace(
            ",", " "
        )  # opcional: espacio como separador
    elif toneladas >= 1:
        return f"{toneladas:,.2f} ton".replace(",", " ")
    else:
        return f"{kg:,.0f} kg".replace(",", " ")
