from app.routes.crud_router import create_crud_router
from app.schemas.control_acceso import CrearControlAcceso, ActualizarControlAcceso, RespuestaControlAcceso
from app.services.control_service import control_acceso_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/controles_acceso",
    service=control_acceso_service,
    create_schema=CrearControlAcceso,
    update_schema=ActualizarControlAcceso,
    read_schema=RespuestaControlAcceso,
    tag="Control de Acceso",
    item_name="control de acceso",
    activate=True,
    update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1]))],
    obtain_deps=[Depends(RoleChecker([1]))]
)
