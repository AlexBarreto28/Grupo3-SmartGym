from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ControlAccesoBase(BaseModel):
    cliente_id: int
    fecha_hora: datetime
    mensaje: Optional[str] = Field(None, max_length=255)

class CrearControlAcceso(BaseModel):
    cedula: str

class ActualizarControlAcceso(BaseModel):
    cliente_id: Optional[int] = None
    fecha_hora: Optional[datetime] = None
    mensaje: Optional[str] = Field(None, max_length=255)

class RespuestaControlAcceso(ControlAccesoBase):
    id: int
    estado: str

    class Config:
        from_attributes = True
