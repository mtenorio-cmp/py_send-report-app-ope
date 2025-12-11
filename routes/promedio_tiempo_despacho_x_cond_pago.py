import logging
from models.requests import DateRangeRequest, DataResponse
from services.documento_query_service import DocumentoQueryService
from services.data_analysis_service import DataAnalysisService

from database.mariadb_connection import MariaDBConnection
from flask import Blueprint, jsonify, request

bp = Blueprint("promedio_tiempo_despacho_x_cond_pago", __name__)
logger = logging.getLogger(__name__)


@bp.route("/data/promedio_tiempo_despacho_x_cond_pago", methods=["POST"])
def get_promedio_tiempo_despacho_x_cond_pago():
    data = DateRangeRequest(**request.get_json())
    # print(request)

    try:
        db = MariaDBConnection()
        db.connect()

        query_service = DocumentoQueryService(db)
        data_analysis_service = DataAnalysisService()

        df_response = query_service.get_delivery_documents_by_date_range(
            start_date=data.start_date,
            end_date=data.end_date,
        )
        # si df_response es vacio, retornar error
        if df_response.empty:
            return jsonify(
                DataResponse(
                    success=False,
                    data=[],
                    rows_count=0,
                    message="No se encontraron documentos",
                ).to_json()
            ), 404

        promedio_tiempo_despacho = data_analysis_service.get_promedio_tiempo_despacho(
            df_response
        )

        # send_message_to_user("6172679210", "¡Consulta realizada con éxito!")
        response_data = DataResponse(
            success=True,
            data={
                "promedio_tiempo_despacho": promedio_tiempo_despacho.to_dict(orient="records"),
            },
            rows_count=len(df_response),
            message="Consulta realizada con éxito!",
        ).to_json()
        return (
            jsonify(response_data),
            200,
        )

    except Exception as e:
        error_response = DataResponse(
            success=False,
            data=None,
            rows_count=0,
            message=str(e),
        ).to_json()
        logger.error(error_response)
        return jsonify(error_response), 500
