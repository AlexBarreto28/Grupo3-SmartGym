from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import RoleChecker, security_scheme, decode_token
from app.db.session import get_db
from app.schemas.pago import CrearPago, ActualizarPago, RespuestaPago
from app.services.pago_service import pago_service
from app.core.exceptions import ReglaNegocioException

# ROUTER PRINCIPAL PARA PAGOS 
router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])

@router.post(
    "/",
    response_model=RespuestaPago,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo pago",
    description="""
    Registra un pago realizado por un cliente para activar su membresía.
    
    **Reglas de negocio:**
    - El pago es inmutable (no se puede modificar después)
    - La fecha se asigna automáticamente
    - La membresía se cambia a "Activo" automáticamente
    - El usuario que registra el pago se obtiene del token JWT
    
    **Roles permitidos:**
    - Finanzas (ID: 3)
    - Administrador (ID: 4)
    """
)
async def crear_pago(
    pago_data: CrearPago,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(security_scheme)
):
    """
    Crea un nuevo pago y activa la membresía asociada.
    """
    # 1. Obtener el usuario autenticado desde el token
    payload = decode_token(token.credentials)
    current_user_id = payload.get("sub") or payload.get("id") or payload.get("usuario_id")
    
    if not current_user_id:
        raise ReglaNegocioException(
            codigo_interno="ERR_USUARIO_NO_AUTENTICADO",
            mensaje="No se pudo obtener el usuario autenticado",
            status_code=401,
        )
    
    # 2. Crear el pago pasando el usuario_id
    obj_in = pago_data.model_dump(exclude_none=True)
    obj_in["current_user_id"] = current_user_id
    
    nuevo_pago = await pago_service.crear(db, obj_in=obj_in)
    
    return nuevo_pago



@router.get(
    "/",
    response_model=list[RespuestaPago],
    dependencies=[Depends(RoleChecker([4, 1]))],  # Admin y Finanzas
    summary="Listar pagos",
    description="Obtiene la lista de todos los pagos registrados"
)
async def listar_pagos(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    data = await pago_service.obtener_paginado(db, skip=skip, limit=size)
    return data["items"]


@router.get(
    "/{pago_id}",
    response_model=RespuestaPago,
    dependencies=[Depends(RoleChecker([4, 1]))],  # Admin y Finanzas
    summary="Obtener un pago por ID"
)
async def obtener_pago(
    pago_id: int,
    db: AsyncSession = Depends(get_db),
):
    pago = await pago_service.obtener(db, pago_id)
    if not pago:
        raise ReglaNegocioException(
            codigo_interno="ERR_PAGO_NO_ENCONTRADO",
            mensaje=f"Pago con ID {pago_id} no encontrado",
            status_code=404,
        )
    return pago


