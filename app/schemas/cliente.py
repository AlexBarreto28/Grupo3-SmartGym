from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date


class UsuarioRelacionResponse(BaseModel):
    id: int
    nombre: str
    email: str

    class Config:
        from_attributes = True


class ClienteBase(BaseModel):
    cedula: str = Field(..., min_length=6, max_length=20)
    telefono: Optional[str] = Field(None, max_length=20)
    fecha_registro: date
    usuario_id: int


class CrearCliente(ClienteBase):
    pass


class RegistrarCliente(BaseModel):
    nombre: str = Field(
        ...,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$",
        examples=["Maria Perez"],
    )
    email: EmailStr
    password: str
    cedula: str = Field(
        ...,
        pattern=r"^V-\d{6,10}$",
        examples=["V-12345678"],
        description="Cédula en formato V-12345678",
    )
    telefono: str = Field(
        ...,
        pattern=r"^\d{11}$",
        examples=["04141234567"],
        description="Número telefónico de 11 dígitos",
    )


class ActualizarCliente(BaseModel):
    cedula: Optional[str] = Field(None, pattern=r"^V-\d{6,10}$")
    telefono: Optional[str] = Field(None, pattern=r"^\d{11}$")
    fecha_registro: Optional[date] = None
    usuario_id: Optional[int] = None


class RespuestaCliente(ClienteBase):
    usuario: Optional[UsuarioRelacionResponse] = None
    estado: str
    id: int

    class Config:
        from_attributes = True
