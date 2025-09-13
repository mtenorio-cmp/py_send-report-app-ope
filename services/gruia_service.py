 
from ast import List
import pandas as pd
import numpy as np
from typing import Dict, Any

import logging

from interfaces.database_interface import IDatabaseConnection
from models.guia_model import GuiaUpdateRequest

logger = logging.getLogger(__name__)

class GuiaService:
    """Servicio para manejo de guías"""

    def __init__(self, db_connection: IDatabaseConnection):
        self.db_connection = db_connection

    def update_multiple_guias(self, request: List[GuiaUpdateRequest]) -> int:
        """
        Actualiza múltiples guías en la base de datos.
        """
        updated_count = 0
        cursor = self.db_connection.cursor()

        for _, row in df.iterrows():
            try:
                update_query = """
                    UPDATE documentos_entrega
                    SET guia_actualizada = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (row['doc_num_gr'], row['doc_id']))
                updated_count += 1
            except Exception as e:
                logger.error(f"Error actualizando guía {row['doc_id']}: {e}")

        self.db_connection.commit()
        cursor.close()
        return updated_count