from app.routes.crud_router import create_crud_router
from app.schemas.membresia_cliente import CrearMembresia, RespuestaMembresia, ActualizarMembresia
from app.services.membresia_service import membresia_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/membresias",
    service=membresia_service,
    create_schema=CrearMembresia,
    update_schema=ActualizarMembresia,
    read_schema=RespuestaMembresia,
    tag="Membresias",
    item_name="membresia",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([1, 3]))],
    create_deps=[Depends(RoleChecker([1, 3]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1, 3]))],
    obtain_deps=[Depends(RoleChecker([1, 3]))]
)
