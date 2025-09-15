from typing import List
from fastapi import APIRouter, HTTPException
import logging
from models.guia_model import GuiaUpdateRequest
from models.requests import DataResponse, ProgradosHoyRequest
 
from services.guia_service import GuiaService
from datetime import datetime, date

from database.mariadb_connection import MariaDBConnection
from services.query_service import SafeQueryService
from services.data_analysis_service import DataAnalysisService
from utils.telegram_utils import send_image_to_telegram, send_message_to_telegram

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
        updated_response = query_service.update_multiple_guias(requests=request)
        print(updated_response)
        # send_message_to_user("6172679210", "¡Consulta realizada con éxito!")
        return updated_response
    except Exception as e:
        logger.error(f"Error en date-range: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/programados_del_dia")
async def programados_hoy(
    request: ProgradosHoyRequest,
):
    try:
        db = MariaDBConnection()
        db.connect()

        query_service = SafeQueryService(db)
        programados = query_service.get_programados_del_dia( request.date_programen)
        if  programados.empty:
            return DataResponse(
                success=True,
                data=None,
                rows_count=0,
                message="No hay datos para la fecha proporcionada.",
            )
        data_analysis_service = DataAnalysisService()
        image_path = data_analysis_service.generar_reporte_imagen(
            df=programados, 
            ruta_salida="reporte_programados_hoy.png",
            date_programen=request.date_programen
            )

        # send_message_to_telegram(image_path)
        date_value = request.date_programen
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, "%d/%m/%Y").date()
        elif isinstance(date_value, date):
            date_obj = date_value.strftime("%d/%m/%y")
        send = send_image_to_telegram(image_path, f"Programacion de despacho del dia {date_obj}")
        print(send)
        return DataResponse(
            success=True,
            data=None,
            rows_count=len(programados),
            message="Consulta realizada con éxito!",
        )
    except Exception as e:
        logger.error(f"Error en date-range: {e}")
        raise HTTPException(status_code=500, detail=str(e))
