from typing import List
from fastapi import APIRouter,  HTTPException
import logging
from models.guia_model import GuiaUpdateRequest
from models.requests import  DataResponse
from services.gruia_service import GuiaService

from database.mariadb_connection import MariaDBConnection

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/data/actualizar_guias_varios")
async def update_guia_many(
    request: List[GuiaUpdateRequest],
):
    # _: bool = Depends(validate_request_auth),
    # query_service: SafeQueryService = Depends(get_query_service),
  

    try:
        db = MariaDBConnection()
        db.connect()

        query_service = GuiaService(db)
        updated_count = query_service.update_multiple_guias(requests=request)

        # send_message_to_user("6172679210", "¡Consulta realizada con éxito!")
        return updated_count
    except Exception as e:
        logger.error(f"Error en date-range: {e}")
        raise HTTPException(status_code=500, detail=str(e))