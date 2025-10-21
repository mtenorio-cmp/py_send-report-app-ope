
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import logging
import os

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
            data = data.dropna(subset=["rd_hora_sal"])
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

    def despachados_del_dia_detallado(
        self,
        df: pd.DataFrame,
        date_programen: date,
        ruta_salida="reporte.png",
    ):
        """
        Recibe un DataFrame con la data de la query
        y genera una tabla estilo el ejemplo en formato imagen.
        """

        # Agrupar por placa y chofer
        grupos = df.groupby(["veh_placa"])
        total_peso = 0
        total_bult = 0

        fig, ax = plt.subplots(
            figsize=(14, len(df) * 0.35)
        )  # ancho mayor y alto dinámico
        # fig.suptitle(
        #     f"Pogramacion de despacho del dia {date_programen}",
        #     fontsize=14,
        #     fontweight="bold",
        #     color="#333333",
        #     y=0.98,
        # )
        ax.axis("off")  # quitar ejes

        # lista para armar tabla matplotlib
        tabla_datos = []
        tabla_cols = [
            "Placa",
            "Chofer",
            "Num Factura",
            "Razón Social",
            "Peso Total",
            "Cantidad Bultos",
        ]

        # construir filas
        subtotal_rows = []
        for placa, datos in grupos:
            subtotal_peso = datos["doc_peso_tot"].sum()
            subtotal_bult = datos["doc_cant_bult"].sum()
            total_peso += subtotal_peso
            total_bult += subtotal_bult

            # detalle
            for _, row in datos.iterrows():
                tabla_datos.append(
                    [
                       f"{'✓' if row['rut_fec_ini'] else '◔'} {row['veh_placa']}",
                        row["chofer_nom_comp"],
                        row["doc_num_fac"],
                        f"{'✓✓' if row['rd_hora_sal'] else ''} {row['doc_raz_soc']}",
                        f"{row['doc_peso_tot']:.2f}",
                        f"{row['doc_cant_bult']:.2f}",
                    ]
                )

            # subtotal (guardar índice para resaltar luego)
            tabla_datos.append(
                [
                    f"Total {placa[0]}",
                    "",
                    "",
                    "",
                    f"{subtotal_peso:.2f}",
                    f"{subtotal_bult:.2f}",
                ]
            )
            subtotal_idx = len(tabla_datos)
            subtotal_rows.append(subtotal_idx)
            tabla_datos.append([""] * len(tabla_cols))  # fila en blanco separadora

        tabla_datos.append(
            [
                "Total General",
                "",
                "",
                "",
                f"{total_peso:.2f}",
                f"{total_bult:.2f}",
            ]
        )
        # crear tabla matplotlib
        table = ax.table(
            cellText=tabla_datos, colLabels=tabla_cols, cellLoc="center", loc="center"
        )

        # estilo
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.2)

        # Alinear Razón Social a la izquierda, Peso y Bultos a la derecha
        nrows = len(tabla_datos) + 1  # +1 por encabezado
        for row in range(1, nrows):
            table[row, 0].set_text_props(ha="left")
            table[row, 1].set_text_props(ha="left")
            table[row, 2].set_text_props(ha="left")
            table[row, 3].set_text_props(ha="left")
            table[row, 4].set_text_props(ha="right")
            table[row, 5].set_text_props(ha="right")

        # resaltar encabezado y bordes
        for (row, col), cell in table.get_celld().items():
            cell.set_linewidth(0.7)
            cell.set_edgecolor("#e0e0e0")
            if row == 0:
                cell.set_facecolor("#3b3b3b")
                cell.set_text_props(color="white", weight="bold")

            # Encabezado Razón Social a la izquierda
            if row == 0 and col == 3:
                cell.set_text_props(ha="left")

            # Encabezado Peso y Bultos a la derecha
            if row == 0 and col in (4, 5):
                cell.set_text_props(ha="right")

            # Subtotal: fondo gris claro y negrita
            if row in subtotal_rows or row == nrows - 1:
                cell.set_facecolor("#e0e0e0")
                cell.set_text_props(weight="bold")

            # if row == nrows - 1:  # Última fila (Total General)
            #     cell.set_facecolor("#e0e0e0")
            #     cell.set_text_props(weight="bold")

        # Ajustar ancho de columna Razón Social
        table.auto_set_column_width([0, 1, 2, 3, 4, 5])

        plt.savefig(ruta_salida, bbox_inches="tight", dpi=200)
        ruta_completa = os.path.abspath(ruta_salida)
        plt.close()
        return ruta_completa
    
   