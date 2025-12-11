from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import random
from utils.palette_colors import PaletteColors, TypePalette


# ==================== Value Objects ====================
@dataclass(frozen=True)
class DonutValue:
    """Representa un valor del donut (inmutable)"""
    value: float
    label: str

    def calculate_percentage(self, total: float) -> float:
        """Calcula el porcentaje respecto al total"""
        return (self.value / total * 100) if total > 0 else 0


@dataclass(frozen=True)
class Position:
    """Representa una posición 2D"""
    x: int
    y: int

    def offset(self, dx: int, dy: int) -> 'Position':
        """Retorna una nueva posición con offset"""
        return Position(self.x + dx, self.y + dy)

    def as_tuple(self) -> Tuple[int, int]:
        """Convierte a tupla para PIL"""
        return (self.x, self.y)


@dataclass(frozen=True)
class TextDimensions:
    """Dimensiones calculadas de un texto"""
    width: int
    height: int


# ==================== Service Layer ====================
class FontProvider:
    """SRP: Responsable únicamente de proveer fuentes"""
    
    def __init__(self, font_name: str):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(self.base_path, font_name) if font_name else os.path.join(self.base_path, "ARIAL.ttf")
        self._cache = {}

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Obtiene una fuente con caché"""
        if size not in self._cache:
            self._cache[size] = ImageFont.truetype(self.font_path, size)
        return self._cache[size]


class ChartGenerator:
    """SRP: Responsable únicamente de generar gráficos matplotlib"""
    
    @staticmethod
    def generate_donut_chart(
        values: List[float],
        colors: List[str],
        size: Tuple[int, int] = (4, 4)
    ) -> str:
        """Genera un gráfico de donut y retorna el nombre del archivo"""
        filename = f"donut_{random.randint(1, 100000)}.png"
        
        fig, ax = plt.subplots(figsize=size, dpi=100)
        ax.pie(values, colors=colors, wedgeprops={"width": 0.30}, startangle=90)
        ax.set(aspect="equal")
        plt.savefig(filename, transparent=True, bbox_inches="tight")
        plt.close()
        
        return filename


class FileManager:
    """SRP: Responsable únicamente de operaciones de archivo"""
    
    @staticmethod
    def load_image(filepath: str) -> Image.Image:
        """Carga una imagen"""
        return Image.open(filepath)
    
    @staticmethod
    def delete_file(filepath: str) -> None:
        """Elimina un archivo de forma segura"""
        if os.path.exists(filepath):
            os.remove(filepath)


class TextMeasurer:
    """SRP: Responsable de medir dimensiones de texto"""
    
    @staticmethod
    def measure_text(
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont
    ) -> TextDimensions:
        """Mide las dimensiones de un texto"""
        bbox = draw.textbbox((0, 0), text, font=font)
        return TextDimensions(
            width=bbox[2] - bbox[0],
            height=bbox[3] - bbox[1]
        )
    
    @staticmethod
    def measure_max_width(
        draw: ImageDraw.ImageDraw,
        texts: List[str],
        fonts: List[ImageFont.FreeTypeFont]
    ) -> int:
        """Calcula el ancho máximo entre varios textos"""
        widths = [
            TextMeasurer.measure_text(draw, text, font).width
            for text, font in zip(texts, fonts)
        ]
        return max(widths) if widths else 0


# ==================== Drawing Strategy ====================
class DonutIndicator:
    """Representa un indicador individual del donut"""
    
    def __init__(
        self,
        value: str,
        label: str,
        percentage: str,
        color: str
    ):
        self.value = value
        self.label = label
        self.percentage = percentage
        self.color = color


class IndicatorRenderer(ABC):
    """OCP: Abierto a extensión, cerrado a modificación"""
    
    def __init__(self, font_provider: FontProvider):
        self.font_provider = font_provider
        self.font_val = font_provider.get_font(28)
        self.font_label = font_provider.get_font(18)
        self.font_pct = font_provider.get_font(22)
    
    @abstractmethod
    def render(
        self,
        draw: ImageDraw.ImageDraw,
        indicators: List[DonutIndicator],
        start_position: Position
    ) -> None:
        """Renderiza los indicadores"""
        pass
    
    def _draw_vertical_bar(
        self,
        draw: ImageDraw.ImageDraw,
        position: Position,
        color: str,
        height: int = 55
    ) -> None:
        """Dibuja una barra vertical"""
        draw.line(
            (position.x, position.y, position.x, position.y + height),
            fill=color,
            width=6
        )
    
    def _draw_indicator_texts(
        self,
        draw: ImageDraw.ImageDraw,
        indicator: DonutIndicator,
        position: Position
    ) -> None:
        """Dibuja los textos de un indicador"""
        text_pos = position.offset(15, 0)
        draw.text(text_pos.as_tuple(), indicator.value, fill=indicator.color, font=self.font_val)
        draw.text(text_pos.offset(0, 32).as_tuple(), indicator.label, fill="#666666", font=self.font_label)


class HorizontalIndicatorRenderer(IndicatorRenderer):
    """LSP: Implementación específica para layout horizontal"""
    
    def render(
        self,
        draw: ImageDraw.ImageDraw,
        indicators: List[DonutIndicator],
        start_position: Position
    ) -> None:
        current_pos = start_position
        
        for indicator in indicators:
            # Calcular ancho del bloque
            text_width = TextMeasurer.measure_max_width(
                draw,
                [indicator.value, indicator.label, indicator.percentage],
                [self.font_val, self.font_label, self.font_pct]
            )
            block_width = text_width + 30
            
            # Dibujar barra y textos
            self._draw_vertical_bar(draw, current_pos, indicator.color)
            self._draw_indicator_texts(draw, indicator, current_pos)
            
            # Dibujar porcentaje
            draw.text(
                current_pos.offset(15, 60).as_tuple(),
                indicator.percentage,
                fill="#777777",
                font=self.font_pct
            )
            
            # Mover horizontalmente
            current_pos = current_pos.offset(block_width, 0)


class VerticalIndicatorRenderer(IndicatorRenderer):
    """LSP: Implementación específica para layout vertical"""
    
    def render(
        self,
        draw: ImageDraw.ImageDraw,
        indicators: List[DonutIndicator],
        start_position: Position
    ) -> None:
        current_pos = start_position
        
        for indicator in indicators:
            # Calcular ancho del bloque
            text_width = TextMeasurer.measure_max_width(
                draw,
                [indicator.value, indicator.label, indicator.percentage],
                [self.font_val, self.font_label, self.font_pct]
            )
            block_width = text_width + 30
            
            # Dibujar barra y textos
            self._draw_vertical_bar(draw, current_pos, indicator.color)
            self._draw_indicator_texts(draw, indicator, current_pos)
            
            # Dibujar separador y porcentaje
            separator_x = current_pos.x + block_width
            draw.line(
                (separator_x, current_pos.y + 30, separator_x, current_pos.y + 50),
                fill="#E5E7EB",
                width=2
            )
            draw.text(
                (separator_x + 15, current_pos.y + 32),
                indicator.percentage,
                fill="#777777",
                font=self.font_pct
            )
            
            # Mover verticalmente
            current_pos = current_pos.offset(0, 75)


# ==================== Facade ====================
class DonutChartBuilder:
    """
    ISP & DIP: Depende de abstracciones, no de concreciones.
    Coordina todos los servicios para construir el donut completo.
    """
    
    def __init__(
        self,
        font_provider: FontProvider,
        chart_generator: ChartGenerator,
        file_manager: FileManager
    ):
        self.font_provider = font_provider
        self.chart_generator = chart_generator
        self.file_manager = file_manager
    
    def _create_indicators(
        self,
        values: List[DonutValue],
        colors: List[str]
    ) -> List[DonutIndicator]:
        """Crea los indicadores a partir de los valores"""
        total = sum(v.value for v in values)
        return [
            DonutIndicator(
                value=str(int(values[i].value)),
                label=values[i].label,
                percentage=f"{values[i].calculate_percentage(total):.2f}%",
                color=colors[i]
            )
            for i in range(len(values))
        ]
    
    def _draw_center_total(
        self,
        draw: ImageDraw.ImageDraw,
        total: float,
        position: Position
    ) -> None:
        """Dibuja el total en el centro del donut"""
        font_big = self.font_provider.get_font(48)
        font_subtitle = self.font_provider.get_font(24)
        
        draw.text(
            position.offset(90, 85).as_tuple(),
            str(int(total)),
            fill="#3A3A3A",
            font=font_big
        )
        draw.text(
            position.offset(100, 140).as_tuple(),
            "Total",
            fill="#777777",
            font=font_subtitle
        )
    
    def build(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        values: List[DonutValue],
        renderer: IndicatorRenderer,
        position: Position = Position(10, 80),
        indicators_offset: Tuple[int, int] = (260, 80)
    ) -> None:
        """Construye el donut completo con el renderer especificado"""
        # Generar colores y valores
        colors = PaletteColors().generate_dynamic_neon_palette(
            len(values),
            mode=TypePalette.LIGHT
        )
        values_list = [v.value for v in values]
        
        # Generar gráfico
        chart_file = self.chart_generator.generate_donut_chart(
            values_list,
            colors,
            size=(3, 3)
        )
        
        try:
            # Cargar y pegar donut
            donut_img = self.file_manager.load_image(chart_file)
            img.paste(donut_img, position.as_tuple(), donut_img)
            
            # Dibujar total en el centro
            self._draw_center_total(draw, sum(values_list), position)
            
            # Crear y renderizar indicadores
            indicators = self._create_indicators(values, colors)
            indicator_pos = position.offset(*indicators_offset)
            renderer.render(draw, indicators, indicator_pos)
            
        finally:
            # Limpiar archivo temporal
            self.file_manager.delete_file(chart_file)


# ==================== API Pública ====================
class ReportDonut:
    """
    Facade simplificado que mantiene compatibilidad con la API original
    """
    
    def __init__(self, font_path: str):
        self.font_provider = FontProvider(font_path)
        self.chart_generator = ChartGenerator()
        self.file_manager = FileManager()
        self.builder = DonutChartBuilder(
            self.font_provider,
            self.chart_generator,
            self.file_manager
        )
    
    def donut_horizontal(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        values: List[DonutValue],
        position: Tuple[int, int] = (10, 80)
    ) -> None:
        """Crea un donut con indicadores horizontales"""
        renderer = HorizontalIndicatorRenderer(self.font_provider)
        self.builder.build(
            img,
            draw,
            values,
            renderer,
            Position(*position),
            indicators_offset=(260, 80)
        )
    
    def donut_vertical(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        values: List[DonutValue],
        position: Tuple[int, int] = (10, 80)
    ) -> None:
        """Crea un donut con indicadores verticales"""
        renderer = VerticalIndicatorRenderer(self.font_provider)
        self.builder.build(
            img,
            draw,
            values,
            renderer,
            Position(*position),
            indicators_offset=(40, 250)
        )