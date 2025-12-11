from typing import List
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from utils.utils import  kg_a_toneladas
 
class RTable:
    def __init__(self, font_path: str):
        self.COLORS = {
            "won": "#10B981",  # Verde
            "negotiation": "#3B82F6",  # Azul
            "libre": "#10B981",
            "en_ruta": "#F59E0B",
            "en_comision": "#8B5CF6",
            "en_mantenimiento": "#EF4444",
            "bg_alt": "#F9FAFB",  # Fondo fila alternada
            "separator": "#E5E7EB",
            "text_primary": "#111827",
            "text_secondary": "#6B7280",
        }

        self.status_colors = {
            "Libre": self.COLORS["libre"],
            "En ruta": self.COLORS["en_ruta"],
            "En comisión": self.COLORS["en_comision"],
            "En mantenimiento": self.COLORS["en_mantenimiento"],
        }

        self.font_title = ImageFont.truetype(font_path, 24)
        self.font_normal = ImageFont.truetype(font_path, 20)
        self.font_badge = ImageFont.truetype(font_path, 16)
        self.font_small = ImageFont.truetype(font_path, 12)

    def generate_table(self, 
    draw: ImageDraw,
    vehiculos: List[str]):
        ROW_HEIGHT = 90
        START_Y = 380
        START_X = 20
        TEXT_START_X = START_X + 5
        WIDTH = 820 + START_X

        # Fuentes
        y = START_Y


        # header
        draw.text(
            (START_X + 500, (y - ROW_HEIGHT) + 55),
            "Rutas",
            fill=self.COLORS["text_secondary"],
            font=self.font_title,
        )
        draw.text(
            (START_X + 730, (y - ROW_HEIGHT) + 55),
            "Fecha",
            fill=self.COLORS["text_secondary"],
            font=self.font_title,
        )
        draw.line(
            [(START_X, (y - ROW_HEIGHT) + 86), (WIDTH, (y - ROW_HEIGHT) + 86)],
            fill=self.COLORS["separator"],
            width=5,
        )

        for i, veh in enumerate(vehiculos):
            row_y = y + i * ROW_HEIGHT

            if i % 2 != 1:
                draw.rectangle([0, row_y, WIDTH, row_y + ROW_HEIGHT], fill=self.COLORS["bg_alt"])

            # Línea divisoria inferior sutil
            draw.line(
                [(START_X, row_y + ROW_HEIGHT), (WIDTH, row_y + ROW_HEIGHT)],
                fill=self.COLORS["separator"],
                width=1,
            )

            # === Placa (nombre principal) ===
            draw.text(
                (TEXT_START_X, row_y + 18),
                veh["placa"],
                fill=self.COLORS["text_primary"],
                font=self.font_title,
            )

            # === Modelo (subtexto gris) ===
            draw.text(
                (TEXT_START_X, row_y + 54),
                veh["modelo"],
                fill=self.COLORS["text_secondary"],
                font=self.font_small,
            )

            # === Badge de Estatus ===
            status = veh["estatus"]
            badge_color = self.status_colors.get(status, "#6B7280")
            badge_text = status.upper()

            # Fondo del badge
            badge_padding = 12
            text_bbox = draw.textbbox((0, 0), badge_text, font=self.font_badge)
            badge_width = text_bbox[2] - text_bbox[0] + badge_padding * 2
            badge_height = 25

            # badge de capacidad x placa
            badge_color_capacidad_x = self.COLORS["text_secondary"]
            badge_capacidad_x = START_X + 130
            badge_text_capacidad_x = f"{kg_a_toneladas(veh['capacidad_despachado'])} / {kg_a_toneladas(veh['capacidad_x_placa'])}"
            text_bbox_capacidad_x = draw.textbbox(
                (0, 0), badge_text_capacidad_x, font=self.font_badge
            )
            badge_width_capacidad_x = (
                text_bbox_capacidad_x[2] - text_bbox_capacidad_x[0] + badge_padding * 2
            )
            draw.rounded_rectangle(
                [
                    badge_capacidad_x,
                    row_y + 15,
                    badge_capacidad_x + badge_width_capacidad_x,
                    row_y + 15 + badge_height,
                ],
                radius=20,
                # fill=badge_color + "20",
                outline=badge_color_capacidad_x,
                width=2,
            )
            draw.text(
                (badge_capacidad_x + badge_padding, row_y + 28),
                badge_text_capacidad_x,
                fill=badge_color_capacidad_x,
                font=self.font_badge,
                anchor="lm",
            )

            # estado de vehiculo
            badge_x = START_X + 320
            draw.rounded_rectangle(
                [badge_x, row_y + 20, badge_x + badge_width, row_y + 20 + badge_height],
                radius=20,
                # fill=badge_color + "20",
                outline=badge_color,
                width=2,
            )
            draw.text(
                (badge_x + badge_padding, row_y + 20 + 15),
                badge_text,
                fill=badge_color,
                font=self.font_badge,
                anchor="lm",
            )

            # === Capacidad despachada ===
            monto = f"{veh['total_vueltas']}"
            draw.text(
                (START_X + 550, row_y + 32),
                monto,
                fill=self.COLORS["text_primary"],
                font=self.font_normal,
            )

            # === Fecha ===
            fecha_inicio = "Salida, Hoy 11:30"
            draw.text(
                (START_X + 800, row_y + 32),
                fecha_inicio,
                fill=self.COLORS["text_secondary"],
                font=self.font_small,
                anchor="rm",
            )

            fecha_fin = "Regreso, Hoy 11:30"
            draw.text(
                (START_X + 800, row_y + 55),
                fecha_fin,
                fill=self.COLORS["text_secondary"],
                font=self.font_small,
                anchor="rm",
            )

        draw.text(
            (START_X, row_y + 110), "Total de capacidad 13.1 t", fill="#555555", font=self.font_small
        )