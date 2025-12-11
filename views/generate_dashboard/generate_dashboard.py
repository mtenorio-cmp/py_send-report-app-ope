import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from .r_table import RTable
from .r_line import RLine
from .r_donut import ReportDonut, DonutValue
from models.tiempo_despacho_resumen import TiempoDespachoResumen
import os
import pandas as pd

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GenerateDashboard:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(self.base_path, "ARIAL.ttf")

        self.WIDTH = 1920
        self.HEIGHT = 1080

        self.img = Image.new("RGB", (self.WIDTH, self.HEIGHT), "white")
        self.draw = ImageDraw.Draw(self.img)

        self.font_title = ImageFont.truetype(self.font_path, 30)
        self.font_subtitle = ImageFont.truetype(self.font_path, 24)
        self.font_small = ImageFont.truetype(self.font_path, 18)
        self.font_big = ImageFont.truetype(self.font_path, 48)

        self.draw.text(
            (50, 40),
            "Estado de vehículos",
            fill="#3A3A3A",
            font=self.font_title,
        )
        self.vehiculos = [
            {
                "placa": "BSR-797",
                "modelo": "PEUGEOT BOXER",
                "porcentaje_del_tal": "12%",
                "total_vueltas": 2,
                "capacidad_x_placa": 1200,
                "capacidad_despachado": 960,
                "capacidad_despachado_porcentaje": "80%",
                "estatus": "Libre",
            },
            {
                "placa": "BSS-795",
                "modelo": "PEUGEOT BOXER",
                "porcentaje_del_tal": "18%",
                "total_vueltas": 3,
                "capacidad_x_placa": 1000,
                "capacidad_despachado": 1150,
                "capacidad_despachado_porcentaje": "115%",
                "estatus": "Libre",
            },
            {
                "placa": "CCA-932",
                "modelo": "PEUGEOT BOXER",
                "porcentaje_del_tal": "9%",
                "total_vueltas": 1,
                "capacidad_x_placa": 1500,
                "capacidad_despachado": 750,
                "capacidad_despachado_porcentaje": "50%",
                "estatus": "En ruta",
            },
            {
                "placa": "BSQ-823",
                "modelo": "PEUGEOT BOXER",
                "porcentaje_del_tal": "21%",
                "total_vueltas": 4,
                "capacidad_x_placa": 1300,
                "capacidad_despachado": 1690,
                "capacidad_despachado_porcentaje": "130%",
                "estatus": "En comisión",
            },
            {
                "placa": "BJU-859",
                "modelo": "PEUGEOT BOXER",
                "porcentaje_del_tal": "6%",
                "total_vueltas": 1,
                "capacidad_x_placa": 1400,
                "capacidad_despachado": 980,
                "capacidad_despachado_porcentaje": "70%",
                "estatus": "En mantenimiento",
            },
        ]

    def init(
        self,
        data_vehiculos: Optional[list] = None,
        data_carga_laboral: Optional[list] = None,
        data_tiempo_promedio: Optional[pd.DataFrame] = None,
        data_exceptions: Optional[pd.DataFrame] = None,
        data_programados_del_dia: Optional[pd.DataFrame] = None,
    ):
        self.draw.text(
            (550, 10),
            "Actualizado 27/11/25 12:30",
            fill="#555555",
            font=self.font_small,
        )
        if data_vehiculos:
            tableReport = RTable(font_path=self.font_path)
            tableReport.generate_table(self.draw, data_vehiculos)

        if data_carga_laboral:
            rLine = RLine(font_path=self.font_path)
            rLine.generate_line(
                self.img,
                line_data=data_carga_laboral,
                position=(900, 20),
                title_x="Fecha",
                title_y="Peso",
            )

        self.draw.rounded_rectangle(
            [900, 500, 1600, 780],
            radius=20,
            fill="#F9FAFB",
            outline="#E5E7EB",
            width=2,
        )

        self.draw.text(
            (920, 520),
            "Pedidos del día",
            fill="#555555",
            font=self.font_title,
        )
        self.draw.text((920, 545), "27/11/25", fill="#999999", font=self.font_subtitle)
        rr = ReportDonut(font_path=self.font_path)
        if not data_programados_del_dia.empty:
            logger.info(data_programados_del_dia)
            rr.donut_horizontal(
                self.img,
                self.draw,
                [
                    DonutValue(value=1, label="Libres"),
                    DonutValue(value=5, label="En comisión"),
                    DonutValue(value=2, label="En ruta"),
                ],
                (900, 550),
            )

        self.draw.rounded_rectangle(
            [900, 800, 1600, 1050],
            radius=20,
            fill="#F9FAFB",
            outline="#E5E7EB",
            width=2,
        )

        if not data_exceptions.empty:
            self.draw.text(
                (1130, 810),
                "Excepciones del mes",
                fill="#555555",
                font=self.font_title,
            )
            values = [
                DonutValue(
                    value=row["count"],
                    label=row["doc_excep"],
                )
                for _, row in data_exceptions.iterrows()
            ]
            rr.donut_horizontal(
                img=self.img,
                draw=self.draw,
                values=values,
                position=(900, 800),
            )

        self.draw.rounded_rectangle(
            [1630, 470, 1910, 1050],
            radius=20,
            fill="#F9FAFB",
            outline="#E5E7EB",
            width=2,
        )

        if not data_tiempo_promedio.empty:
            # agrupa por promedio_plazo_hrs y suma por cantidad_registros luego convertir a DonutValue
            grouped = data_tiempo_promedio.groupby(
                "promedio_plazo_hrs", as_index=False
            )["cantidad_registros"].sum()

            values = [
                DonutValue(
                    value=row["cantidad_registros"],
                    label=(
                        "Otros"
                        if row["promedio_plazo_hrs"] == 0
                        else f"{int(row['promedio_plazo_hrs'])} Horas"
                    ),
                )
                for _, row in grouped.iterrows()
            ]
            rr.donut_vertical(
                img=self.img,
                draw=self.draw,
                values=values,
                position=(1630, 450),
            )

        self.img.save("dashboard_1920x1080.png", quality=95)
