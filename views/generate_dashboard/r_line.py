from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from PIL import Image
from utils.utils import kg_a_toneladas
import matplotlib.dates as mdates
import datetime as dt
import io


class RLine:
    def __init__(self, font_path: str):
        self.font_path = font_path

    def generate_line(
        self,
        img: Image,
        line_data: List[Dict[float, dt.datetime]],
        position: Tuple[int, int] = (10, 80),
        title_x: str = "",
        title_y: str = "",
        meta_alta: int = 0,
        meta_media: int = 0,
    ):
        # Líneas objetivo

        verde_oscuro = "#22C55E"  # Verde principal
        verde_claro = "#86EFAC"
        amarillo_claro = "#FEF08A"
        naranja_suave = "#FDBA74"
        rojo_suave = "#FCA5A5"
        gris_fondo = "#F9FAFB"
        texto_principal = "#1F2937"
        texto_secundario = "#6B7280"

        plt.rcParams.update(
            {
                "font.family": "Segoe UI",  # o 'Inter', 'SF Pro', 'Arial'
                "font.size": 14,
            }
        )

        fig, ax = plt.subplots(figsize=(15, 7))
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor(gris_fondo)

        fechas = [item["fecha"] for item in line_data]
        pesos = [item["peso"] for item in line_data]

        # Línea principal con degradado visual
        line = ax.plot(
            fechas,
            pesos,
            color=verde_oscuro,
            linewidth=4.5,
            marker="o",
            markersize=6,
            markerfacecolor=verde_claro,
            markeredgecolor=verde_oscuro,
            markeredgewidth=2,
        )

        # Área bajo la curva
        ax.fill_between(fechas, pesos, alpha=0.18, color=verde_oscuro)

        # Líneas de referencia
        if meta_alta > 0:
            ax.axhline(
                meta_alta,
                color=rojo_suave,
                linewidth=2.5,
                alpha=0.8,
                linestyle="--",
            )
            ax.text(
                fechas[0],
                meta_alta + 600,
                "Meta Alta: " + kg_a_toneladas(meta_alta),
                color="#DC2626",
                fontsize=11,
                fontweight="bold",
            )
            
        if meta_media > 0:
            ax.axhline(
                meta_media,
                color=naranja_suave,
                linewidth=2.5,
                alpha=0.8,
                linestyle="--",
            )
            ax.text(
                fechas[0],
                meta_media + 600,
                "Meta Media: " + kg_a_toneladas(meta_media),
                color="#F97316",
                fontsize=11,
                fontweight="bold",
            )

        # # Título grande y limpio
        # ax.set_title(
        #     "CARGA LABORAL POR TONELADAS",
        #     fontsize=18,
        #     fontweight="bold",
        #     color=texto_principal,
        #     pad=30,
        # )

        # Etiquetas
        ax.set_ylabel(
            title_y,
            fontsize=16,
            color=texto_secundario,
            labelpad=15,
        )
        ax.set_xlabel(
            title_x,
            fontsize=16,
            color=texto_secundario,
            labelpad=15,
        )

        # Formato del eje X (día + mes abreviado)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.tick_params(axis="x", which="major", labelsize=14, colors=texto_secundario)
        ax.tick_params(axis="y", which="major", labelsize=14, colors=texto_secundario)

        # Quitar bordes superiores y derechos (estilo moderno)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#E5E7EB")
        ax.spines["bottom"].set_color("#E5E7EB")

        # Grid suave
        ax.grid(True, color="white", linewidth=1.5, alpha=0.7)
        ax.set_axisbelow(True)

        # Valor actual destacado
        ultimo_peso = pesos[-1]
        ultimo_fecha = fechas[-1]
        ax.annotate(
            kg_a_toneladas(ultimo_peso),
            xy=(ultimo_fecha, ultimo_peso),
            xytext=(10, 15),
            textcoords="offset points",
            fontsize=14,
            fontweight="bold",
            color=verde_oscuro,
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=verde_claro,
                alpha=0.9,
                edgecolor=verde_oscuro,
            ),
        )

        # Ajustes finales
        plt.tight_layout(pad=3.0)

        # Guardar con alta calidad

        buf = io.BytesIO()
        plt.savefig(
            buf,
            format="png",
            dpi=72,
            bbox_inches="tight",
            facecolor="#FFFFFF",
            edgecolor="none",
        )
        buf.seek(0)
        plot_image = Image.open(buf)
        img.paste(plot_image, position)
        plt.close(fig)
