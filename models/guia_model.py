from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import date


class GuiaUpdateRequest(BaseModel):
    fact_serie: str = Field(..., description="Serie de la factura")
    fact_num: int = Field(..., description="Numero de la factura")
    guia_serie: str = Field(default=None, description="serie de la guía")
    guia_num: int = Field(default=None,description="Numero de la guía")
    guia_fecha: date = Field(default=None, description="Fecha programada de la guía")
    guia_program_fecha: date = Field(default=None, description="Fecha programada de la guía")
    guia_agencia: Optional[str] = Field(default=None, description="Agencia de la guía")
    
