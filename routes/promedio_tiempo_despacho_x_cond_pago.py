from fastapi import APIRouter,  HTTPException
import logging
from models.requests import DateRangeRequest, DataResponse
from services.query_service import SafeQueryService
from services.data_analysis_service import DataAnalysisService

from database.mariadb_connection import MariaDBConnection

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/data/promedio_tiempo_despacho_x_cond_pago")
async def get_promedio_tiempo_despacho_x_cond_pago(
    request: DateRangeRequest,
):
    # _: bool = Depends(validate_request_auth),
    # query_service: SafeQueryService = Depends(get_query_service),
  

    try:
        db = MariaDBConnection()
        db.connect()

        query_service = SafeQueryService(db)
        data_analysis_service = DataAnalysisService()

        df_response = query_service.get_delivery_documents_by_date_range(
            start_date=request.start_date,
            end_date=request.end_date,
            # motivos_list=motivos,
        )
        
        promedio_tiempo_despacho = data_analysis_service.get_promedio_tiempo_despacho(df_response)

        # send_message_to_user("6172679210", "¡Consulta realizada con éxito!")
        return DataResponse(
            **{
                "success": True,
                "data": {
                    "promedio_tiempo_despacho": promedio_tiempo_despacho,
                },
                "rows_count": len(df_response),
                "message": "Consulta realizada con éxito!",
            }
        )
    except Exception as e:
        logger.error(f"Error en date-range: {e}")
        raise HTTPException(status_code=500, detail=str(e))
