from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import date


class DateRangeRequest(BaseModel):
    start_date: date = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    end_date: date = Field(..., description="Fecha de fin (YYYY-MM-DD)")
    # table_name: str = Field(..., description="Nombre de la tabla a consultar")
    # date_column: str = Field(default="created_at", description="Columna de fecha a filtrar")
    # columns: Optional[List[str]] = Field(default=None, description="Columnas específicas a obtener")
    # limit: Optional[int] = Field(default=1000, ge=1, le=10000, description="Límite de registros")
    # analysis_type: Optional[str] = Field(default="basic", description="Tipo de análisis: basic, full")

    # @field_validator('end_date', 'start_date')
    # def validate_date_range(cls, v, values):
    #     if values.data['end_date'] < values.data['start_date']:
    #         raise ValueError('end_date debe ser mayor o igual que start_date')
    #     return v


class UserActivityRequest(BaseModel):
    user_id: Optional[int] = Field(
        default=None, description="ID del usuario específico"
    )
    start_date: date = Field(..., description="Fecha de inicio")
    end_date: date = Field(..., description="Fecha de fin")
    activity_type: Optional[str] = Field(default=None, description="Tipo de actividad")
    limit: Optional[int] = Field(default=500, ge=1, le=5000)


class SalesReportRequest(BaseModel):
    start_date: date = Field(..., description="Fecha de inicio")
    end_date: date = Field(..., description="Fecha de fin")
    product_id: Optional[int] = Field(
        default=None, description="ID del producto específico"
    )
    region: Optional[str] = Field(default=None, description="Región específica")
    group_by: Optional[str] = Field(
        default="date", description="Agrupar por: date, product, region"
    )
    limit: Optional[int] = Field(default=1000, ge=1, le=10000)


class DataResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    rows_count: Optional[int] = None

    def to_json(self):
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "rows_count": self.rows_count,
        }


class ProgradosHoyRequest(BaseModel):
    date_programen: date = Field(..., description="Fecha (YYYY-MM-DD)")
