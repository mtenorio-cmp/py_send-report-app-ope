from dataclasses import dataclass

@dataclass
class TiempoDespachoResumen:
    doc_con_pag: str
    cantidad_registros: int
    promedio_plazo_hrs: float
    promedio_tiempo_despacho: str
    porcentaje: float
    suma_porcentaje_plazo: float
