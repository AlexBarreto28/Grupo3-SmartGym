from app.routes.crud_router import create_crud_router
from app.schemas.cliente import RegistrarCliente, ActualizarCliente, RespuestaCliente
from app.schemas.evaluacion_biometrica import RespuestaEvaluacion  
from app.services.cliente_service import cliente_service
from app.services.evaluacion_service import evaluacion_service  
from fastapi import Depends, APIRouter  
from app.core.deps import RoleChecker
from app.db.session import get_db  
from sqlalchemy.ext.asyncio import AsyncSession  
from sqlalchemy import select, desc  
from app.models.evaluacion_biometrica import EvaluacionBiometrica  
from app.core.exceptions import ReglaNegocioException  

# Router para el endpoint personalizado
custom_router = APIRouter(prefix="/api/v1/clientes", tags=["Cliente"])

@custom_router.get(
    "/{cliente_id}/evaluaciones",
    response_model=list[RespuestaEvaluacion],
    summary="Obtener historial de evaluaciones de un cliente",
    description="Retorna todas las evaluaciones biométricas de un cliente, ordenadas cronológicamente (más reciente primero)"
)
async def get_historial_evaluaciones(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(RoleChecker([1, 2]))  
):

    # Consultar evaluaciones del cliente ordenadas por fecha descendente
    result = await db.execute(
        select(EvaluacionBiometrica)
        .where(EvaluacionBiometrica.cliente_id == cliente_id)
        .where(EvaluacionBiometrica.estado == "activo")
        .order_by(desc(EvaluacionBiometrica.fecha))
    )
    evaluaciones = result.scalars().all()
    
    if not evaluaciones:
        raise ReglaNegocioException(
            codigo_interno="ERR_SIN_EVALUACIONES",
            mensaje=f"No se encontraron evaluaciones para el cliente con ID {cliente_id}",
            status_code=404,
        )
    
    return evaluaciones

router = create_crud_router(
    prefix="/api/v1/clientes",
    service=cliente_service,
    create_schema=RegistrarCliente,
    update_schema=ActualizarCliente,
    read_schema=RespuestaCliente,
    tag="Cliente",
    item_name="Cliente",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1]))],
    obtain_deps=[Depends(RoleChecker([1, 2]))]
)
