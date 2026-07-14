from app.routes.crud_router import create_crud_router
from app.schemas.maquina import CrearMaquina, RespuestaMaquina, ActualizarMaquina
from app.schemas.estado import CambiarEstado
from app.services.maquina_service import maquina_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/maquinas",
    service=maquina_service,
    create_schema=CrearMaquina,
    update_schema=ActualizarMaquina,
    read_schema=RespuestaMaquina,
    tag="Maquinas",
    item_name="máquina",
    allow_delete=False,
    state_schema=CambiarEstado,
    update_deps=[Depends(RoleChecker([1, 2]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1, 2]))],
    obtain_deps=[Depends(RoleChecker([1, 2]))]
)
