import logging

from interfaces.database_interface import IDatabaseConnection
from models.guia_model import GuiaUpdateRequest
from typing import List

from models.requests import DataResponse

logger = logging.getLogger(__name__)


class GuiaService:
    """Servicio para manejo de guías"""

    def __init__(self, db_connection: IDatabaseConnection):
        self.db_connection = db_connection

    def update_multiple_guias(self, requests: List[GuiaUpdateRequest]) -> DataResponse:
        """
        Actualiza múltiples guías en la base de datos usando fact_num y fact_serie como condición.
        Retorna la cantidad de filas actualizadas.
        """
        updated_count = 0
        errors = []
        update_query = """
            UPDATE documentos 
            SET NumeroGR = %(guia_num)s, 
                SerieGR = %(guia_serie)s, 
                FechaEntregaGR = %(guia_date)s, 
                AgenciaTransporte = %(guia_agencia)s 
            WHERE 
                NumeroFactura = %(fact_num)s AND 
                SerieFactura = %(fact_serie)s
        """
        try:
            with self.db_connection.get_cursor() as cursor:
                for guia in requests:
                    try:
                        params = {
                           "guia_num": guia.guia_num,
                           "guia_serie": guia.guia_serie,
                           "guia_date": guia.guia_date,
                           "guia_agencia": guia.guia_agencia,
                           "fact_num": guia.fact_num,
                           "fact_serie": guia.fact_serie,
                        }
                        cursor.execute(update_query, params)
                        updated_count += 1
                    except Exception as e:
                        error_msg = f"Error actualizando guía fact_num={guia.fact_num}, fact_serie={guia.fact_serie}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
            # Commit si no hay errores
            if len(errors) == 0:
                self.db_connection.connection.commit()
            else:
                self.db_connection.connection.rollback()
        except Exception as e:
            logger.error(f"Error en la transacción de actualización masiva: {e}")
            errors.append(f"Error en la transacción: {e}")
        return {
            "success": len(errors) == 0,
            "data": errors,
            "message": "",
            "rows_count": updated_count,
        }
