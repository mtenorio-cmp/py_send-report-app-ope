import pandas as pd
import numpy as np
from typing import Dict, Any

import logging

logger = logging.getLogger(__name__)


class DataAnalysisService:
    """Servicio para análisis de datos usando pandas y numpy"""

    def get_promedio_tiempo_despacho(self, data: pd.DataFrame) -> list[dict]:
        """Obtiene estadísticas resumidas del DataFrame"""

        condicones_pago = [
            "Contado contra entrega;24",
            "CERC;24",
            "FACT 90 - 1;24",
            "FACT 90 - 2;24",
            "FACT 90 - 3;48",
            "FACT 90 - 4;48",
            "FACT 90 - 5;48",
            "LETRAS 365 - 1;24",
            "LETRAS 365 - 3;24",
            "LETRAS 365 - 5;48",
            "PA5050;72",
            "PADEL;24",
            "ACUADEL;24",
            "PADEL 96;72",
            "Pago Adelantado;24",
            "PA72;48",
        ]
        try:
            data = data.dropna(subset=['rd_hora_sal'])
            data["rd_hora_sal"] = pd.to_datetime(data["rd_hora_sal"])
            data["doc_fec_crea"] = pd.to_datetime(data["doc_fec_crea"])
            data["tiempo_despacho"] = data["rd_hora_sal"] - data["doc_fec_crea"]

            condiciones_map = {}
            for item in condicones_pago:
                key, value = item.split(";")
                condiciones_map[key] = int(value)

            data["plazo_hrs"] = data["doc_con_pag"].map(condiciones_map)

            grouped_data = (
                data.groupby("doc_con_pag")
                .agg(
                    cantidad_registros=("doc_con_pag", "size"),
                    promedio_plazo_hrs=("plazo_hrs", "mean"),
                    promedio_tiempo_despacho=("tiempo_despacho", "mean"),
                )
                .reset_index()
            )

            total_registros = data.shape[0]
            grouped_data["porcentaje"] = (
                grouped_data["cantidad_registros"] / total_registros
            ) * 100
            grouped_data["suma_porcentaje_plazo"] = grouped_data.groupby(
                "promedio_plazo_hrs"
            )["porcentaje"].transform("sum")

            # Format the timedelta to the desired string format for promedio_tiempo_despacho
            grouped_data["promedio_tiempo_despacho"] = grouped_data[
                "promedio_tiempo_despacho"
            ].apply(
                lambda x: f"{x.days:02d} Días {x.seconds // 3600:02d} Hrs {(x.seconds % 3600) // 60:02d} Mins"
            )

            return [] if grouped_data.empty else grouped_data.to_dict("records")

        except Exception as e:
            logger.error(f"Error calculando estadísticas: {e}")
            raise
