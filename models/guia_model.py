from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import date


class GuiaUpdateRequest(BaseModel):
    guia_num: int = Field(description="Numero de la guía")
    guia_serie: str = Field(description="serie de la guía")
    guia_date: date = Field(..., description="Fecha de guía")
    guia_agencia: Optional[str] = Field(..., description="Agencia de la guía")
    
    fact_num: int = Field(default=None, description="ID de la factura")
    fact_serie: str = Field(default=None, description="Serie de la factura")
