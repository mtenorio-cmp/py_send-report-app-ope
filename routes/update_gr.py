from ast import List
from fastapi import APIRouter,  HTTPException
import logging
from models.guia_model import GuiaUpdateRequest
from models.requests import  DataResponse
from services.query_service import SafeQueryService
from services.data_analysis_service import DataAnalysisService

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

        query_service = SafeQueryService(db)
        data_analysis_service = DataAnalysisService()

        df_response = query_service.get_delivery_documents_by_date_range(
            start_date=request.start_date,
            end_date=request.end_date,
            # motivos_list=motivos,
        )
        
        updated_count = query_service.update_multiple_guias(df_response)

        # send_message_to_user("6172679210", "¡Consulta realizada con éxito!")
        return DataResponse(
            **{
                "success": True,
                "data": {
                    "updated_count": updated_count,
                },
                "rows_count": len(df_response),
                "message": "Actualización realizada con éxito!",
            }
        )
    except Exception as e:
        logger.error(f"Error en date-range: {e}")
        raise HTTPException(status_code=500, detail=str(e))