from app.routes.crud_router import create_crud_router
from app.schemas.cliente import CrearCliente, ActualizarCliente, RespuestaCliente
from app.services.cliente_service import cliente_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/clientes",
    service=cliente_service,
    create_schema=CrearCliente,
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
