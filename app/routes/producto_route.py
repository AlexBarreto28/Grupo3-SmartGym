from app.routes.crud_router import create_crud_router
from app.schemas.producto_tienda import CrearProducto, ActualizarProducto, RespuestaProducto
from app.services.producto_service import producto
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/productos",
    service=producto,
    create_schema=CrearProducto,
    update_schema=ActualizarProducto,
    read_schema=RespuestaProducto,
    tag="Productos",
    item_name="producto",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1]))],
    obtain_deps=[Depends(RoleChecker([1]))]
)
