from app.routes.crud_router import create_crud_router
from app.schemas.rol import CrearRol, ActualizarRol, RespuestaRol
from app.services.roles_service import rol_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/roles",
    service=rol_service,
    create_schema=CrearRol,
    update_schema=ActualizarRol,
    read_schema=RespuestaRol,
    tag="Roles",
    item_name="rol",
    activate=True,
        update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1]))],
    obtain_deps=[Depends(RoleChecker([1]))]
)
