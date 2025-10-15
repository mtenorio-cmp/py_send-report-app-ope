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
        avisos = []
        try:
            with self.db_connection.get_cursor() as cursor:
                for doc in requests:
                    try:
                        set_clauses = []
                        params = {}
                        if doc.guia_num is not None:
                            set_clauses.append("NumeroGR = %(guia_num)s")
                            params["guia_num"] = doc.guia_num
                        if doc.guia_serie is not None:
                            set_clauses.append("SerieGR = %(guia_serie)s")
                            params["guia_serie"] = doc.guia_serie
                        if hasattr(doc, "guia_fecha") and doc.guia_fecha is not None:
                            set_clauses.append("FechaEmisionGR = %(guia_fecha)s")
                            params["guia_fecha"] = doc.guia_fecha
                        if hasattr(doc, "guia_program_fecha") and doc.guia_program_fecha is not None:
                            set_clauses.append("FechaEntregaGR = %(guia_program_fecha)s")
                            
                        if hasattr(doc, "guia_program_fecha") and doc.guia_program_fecha is not None:
                            set_clauses.append("FechaProgramadaGR = %(guia_program_fecha)s")
                            params["guia_program_fecha"] = doc.guia_program_fecha
                        if doc.guia_agencia is not None:
                            set_clauses.append("AgenciaTransporte = %(guia_agencia)s")
                            params["guia_agencia"] = doc.guia_agencia
                        # Si no hay campos a actualizar, saltar
                        if not set_clauses:
                            continue
                        params["fact_num"] = doc.fact_num
                        params["fact_serie"] = doc.fact_serie
                        update_query = f"""
                            UPDATE documentos 
                            SET {', '.join(set_clauses)}
                            WHERE NumeroFactura = %(fact_num)s AND SerieFactura = %(fact_serie)s
                        """
                        cursor.execute(update_query, params)
                        if cursor.rowcount == 0:
                            aviso = f"No se encontro documento para {doc.fact_serie}-{doc.fact_num}. No se actualizo ninguna fila."
                            logger.warning(aviso)
                            avisos.append(aviso)
                        else:
                            updated_count += 1
                    except Exception as e:
                        error_msg = f"Error actualizando guia para la FT {doc.fact_serie}-{doc.fact_num}: {e}"
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
        finally:
            try:
                self.db_connection.disconnect()
            except Exception as e:
                logger.error(f"Error cerrando la conexión a la base de datos: {e}")
        if len(errors) == 0 and len(avisos) > 0:
            message = "Actualizacion masiva realizada parcialmente. Algunos documentos no se encontraron."
        elif len(errors) == 0:
            message = "Actualizacion masiva realizada con exito!"
        else:
            message = "Error en la actualizacion masiva."
        return {
            "success": len(errors) == 0 and len(avisos) == 0,
            "data": {"errores": errors, "avisos": avisos},
            "message": message,
            "rows_count": updated_count,
        }
