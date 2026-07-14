from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional

class MaquinaRelacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str 
    descripcion: str 


class TicketBase(BaseModel):
    descripcion: str = Field(..., min_length=5, max_length=255)
    maquina_id: int
    usuario_id: int

class CrearTicket(TicketBase):
    fecha_apertura: datetime
    fecha_cierre: datetime
    costo: float = Field(..., ge=0)

class ActualizarTicket(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=5, max_length=255)
    maquina_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha_cierre: Optional[datetime] = None
    costo: Optional[float] = Field(None, ge=0)
    estado: Optional[str] = None

class CerrarTicket(BaseModel):
    costo: float = Field(..., ge=0)

class RespuestaTicket(TicketBase):
    id: int
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime] = None
    costo: Optional[float] = None
    maquina: Optional[MaquinaRelacionResponse] = None
    estado: str

    class Config:
        from_attributes = True
