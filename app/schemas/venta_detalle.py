from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class ProductoRelacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal = Field(..., decimal_places=2, ge=0)
class DetalleVentaBase(BaseModel):
    venta_id: int
    producto_id: int
    cantidad: int = Field(..., gt=0)

class CrearDetalleVenta(DetalleVentaBase):
    pass

class ActualizarDetalleVenta(BaseModel):
    venta_id: Optional[int] = None
    producto_id: Optional[int] = None
    cantidad: Optional[int] = Field(None, gt=0)
    estado: Optional[str] = None

class RespuestaDetalleVenta(DetalleVentaBase):
    id: int
    estado: str
    producto: Optional[ProductoRelacionResponse] = None
    class Config:
        from_attributes = True
