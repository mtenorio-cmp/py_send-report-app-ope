import random
import colorsys


class TypePalette:
    LIGHT = "light"
    DARK = "dark"


class PaletteColors:
    def hsl_to_hex(self, h, s, l):
        """Convierte valores HSL (0-1) a HEX."""
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

    def generate_dynamic_neon_palette(
        self,
        n_colors: int = 15,
        mode: TypePalette = TypePalette.LIGHT,
    ):
        """
        Genera colores estilo NEÓN dinámicos, adaptados para modo LIGHT o DARK.
        """
        palette = []

        for _ in range(n_colors):
            # Hue en todo el espectro (0–1)
            h = random.random()

            if mode == TypePalette.LIGHT:
                s = random.uniform(0.70, 0.95)  # saturación vibrante
                l = random.uniform(0.50, 0.70)  # luminosidad media-alta
            elif mode == TypePalette.DARK:
                s = random.uniform(0.80, 1.00)  # aún más saturado
                l = random.uniform(0.35, 0.55)  # luminosidad media-baja
            else:
                raise ValueError("El modo debe ser 'light' o 'dark'")

            palette.append(self.hsl_to_hex(h, s, l))

        random.shuffle(palette)

        return palette
