from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class CrearDetalleVenta(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)

class VentaBase(BaseModel):
    cliente_id: int

class CrearVenta(VentaBase):
    detalles: List[CrearDetalleVenta] = Field(..., min_length=1)

class ActualizarVenta(BaseModel):
    estado: Optional[str] = None

class RespuestaVenta(BaseModel):
    id: int
    cliente_id: int
    total: float
    fecha_venta: datetime
    estado: str

    class Config:
        from_attributes = True
