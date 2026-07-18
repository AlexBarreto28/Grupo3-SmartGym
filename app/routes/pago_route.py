from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import RoleChecker, security_scheme, decode_token
from app.db.session import get_db
from app.schemas.pago import CrearPago, ActualizarPago, RespuestaPago
from app.services.pago_service import pago_service
from app.core.exceptions import ReglaNegocioException
import math


# ROUTER PERSONALIZADO PARA PAGOS
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
    # 1. Decodificar el token para obtener el usuario autenticado
    payload = decode_token(token.credentials)
    current_user_id = payload.get("sub") or payload.get("id") or payload.get("usuario_id")
    
    if not current_user_id:
        raise ReglaNegocioException(
            codigo_interno="ERR_USUARIO_NO_AUTENTICADO",
            mensaje="No se pudo obtener el usuario autenticado",
            status_code=401,
        )
    
    # 2. Preparar los datos para el servicio
    obj_in = pago_data.model_dump(exclude_none=True)
    obj_in["current_user_id"] = current_user_id  
    
    # 3. Crear el pago
    nuevo_pago = await pago_service.crear(db, obj_in=obj_in)
    
    return nuevo_pago

@router.get(
    "/",
    response_model=dict,
    dependencies=[Depends(RoleChecker([4, 1]))],  # Admin (4) y Finanzas (1)
    summary="Listar pagos",
    description="Obtiene la lista de todos los pagos registrados con paginación"
)
async def listar_pagos(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Resultados por página"),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    
    data = await pago_service.obtener_paginado(
        db,
        skip=skip,
        limit=size,
        filters={}
    )
    
    return {
        "page": page,
        "size": size,
        "total": data["total"],
        "pages": math.ceil(data["total"] / size),
        "items": [
            RespuestaPago.model_validate(item)
            for item in data["items"]
        ]
    }



@router.get(
    "/{pago_id}",
    response_model=RespuestaPago,
    dependencies=[Depends(RoleChecker([4, 1]))],  # Admin (4) y Finanzas (1)
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



@router.get(
    "/membresia/{membresia_id}",
    response_model=list[RespuestaPago],
    dependencies=[Depends(RoleChecker([4, 1]))],
    summary="Obtener pagos por membresía",
    description="Retorna todos los pagos asociados a una membresía específica"
)
async def listar_pagos_por_membresia(
    membresia_id: int,
    db: AsyncSession = Depends(get_db),
):
    data = await pago_service.obtener_paginado(
        db,
        skip=0,
        limit=100,
        filters={"membresia_id": membresia_id}
    )
    
    return data["items"]


@router.get(
    "/cliente/{cliente_id}",
    response_model=list[RespuestaPago],
    dependencies=[Depends(RoleChecker([4, 1]))],
    summary="Obtener pagos por cliente",
    description="Retorna todos los pagos asociados a un cliente específico"
)
async def listar_pagos_por_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Buscar todas las membresías del cliente
    from app.models.membresia_cliente import MembresiaCliente
    from sqlalchemy import select
    
    result = await db.execute(
        select(MembresiaCliente.id).where(MembresiaCliente.cliente_id == cliente_id)
    )
    membresia_ids = [row[0] for row in result.all()]
    
    if not membresia_ids:
        raise ReglaNegocioException(
            codigo_interno="ERR_SIN_MEMBRESIAS",
            mensaje=f"El cliente con ID {cliente_id} no tiene membresías asociadas",
            status_code=404,
        )
    
    data = await pago_service.obtener_paginado(
        db,
        skip=0,
        limit=100,
        filters={"membresia_id__in": membresia_ids}
    )
    
    return data["items"]