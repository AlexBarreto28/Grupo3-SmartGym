from app.routes.crud_router import create_crud_router
from app.schemas.usuario import CrearUsuario, ActualizarUsuario, RespuestaUsuario
from app.services.usuario_service import usuario_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/usuarios",
    service=usuario_service,
    create_schema=CrearUsuario,
    update_schema=ActualizarUsuario,
    read_schema=RespuestaUsuario,
    tag="Usuarios",
    item_name="usuario",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1]))],
    obtain_deps=[Depends(RoleChecker([1, 2, 3, 4]))]
)
