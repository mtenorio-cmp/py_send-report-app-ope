from typing import List
import logging
from models.guia_model import GuiaUpdateRequest
from models.requests import DataResponse, ProgradosHoyRequest

from services.guia_service import GuiaService
from datetime import datetime, date

from database.mariadb_connection import MariaDBConnection
from services.documento_query_service import DocumentoQueryService
from services.data_analysis_service import DataAnalysisService
from utils.telegram_utils import send_image_to_telegram, send_message_to_telegram
from flask import Blueprint, jsonify, request

bp = Blueprint("guia", __name__)
logger = logging.getLogger(__name__)


@bp.route("/data/actualizar_guias_varios", methods=["POST"])
def update_guia_many():
    # _: bool = Depends(validate_request_auth),
    # query_service: SafeQueryService = Depends(get_query_service),

    try:
        requestList = [GuiaUpdateRequest(**item) for item in request.get_json()]
        db = MariaDBConnection()
        db.connect()

        query_service = GuiaService(db)
        updated_response = query_service.update_multiple_guias(requests=requestList)
        return jsonify(updated_response), 200
    except Exception as e:
        respose = DataResponse(
            success=False,
            data=None,
            rows_count=0,
            message=str(e),
        ).to_json()
        logger.error(respose)
        return jsonify(respose), 500


@bp.route("/report/programados_del_dia")
def programados_hoy():
    try:
        db = MariaDBConnection()
        db.connect()

        query_service = GuiaService(db)
        programados = query_service.get_guias_by_fecha_programada(filters={})
    #         if  programados.empty:
    #             return DataResponse(
    #                 success=True,
    #                 data=None,
    #                 rows_count=0,
    #                 message="No hay datos para la fecha proporcionada.",
    #             )
    #         data_analysis_service = DataAnalysisService()
    #         image_path = data_analysis_service.generar_reporte_imagen(
    #             df=programados,
    #             ruta_salida="reporte_programados_hoy.png",
    #             date_programen=request.date_programen
    #             )

    #         # send_message_to_telegram(image_path)
    #         date_value = request.date_programen
    #         if isinstance(date_value, str):
    #             date_obj = datetime.strptime(date_value, "%d/%m/%Y").date()
    #         elif isinstance(date_value, date):
    #             date_obj = date_value.strftime("%d/%m/%y")
    #         send = send_image_to_telegram(image_path, f"Programacion de despacho del dia {date_obj}")
    #         print(send)
    #         return DataResponse(
    #             success=True,
    #             data=None,
    #             rows_count=len(programados),
    #             message="Consulta realizada con éxito!",
    #         )
    except Exception as e:
        logger.error(f"Error en date-range: {e}")


#         raise HTTPException(status_code=500, detail=str(e))
