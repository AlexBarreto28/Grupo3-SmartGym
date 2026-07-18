from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class EvaluacionBase(BaseModel):
    peso: float = Field(..., gt=0)
    estatura: float = Field(..., gt=0)
    porcentaje_grasa: float = Field(..., ge=0, le=100)
    observaciones: Optional[str] = Field(None, max_length=255)
    cliente_id: int

class CrearEvaluacion(EvaluacionBase):
    pass

class ActualizarEvaluacion(BaseModel):
    peso: Optional[float] = Field(None, gt=0)
    estatura: Optional[float] = Field(None, gt=0)
    porcentaje_grasa: Optional[float] = Field(None, ge=0, le=100)
    observaciones: Optional[str] = Field(None, max_length=255)
    cliente_id: Optional[int] = None

class RespuestaEvaluacion(EvaluacionBase):
    id: int 
    fecha: date  
    peso: float
    estatura: float
    porcentaje_grasa: float
    observaciones: Optional[str] = None
    cliente_id: int
    estado: str

    class Config:
        from_attributes = True
