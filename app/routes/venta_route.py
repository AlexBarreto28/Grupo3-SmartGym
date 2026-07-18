from app.routes.crud_router import create_crud_router
from app.schemas.venta_tienda import CrearVenta, ActualizarVenta, RespuestaVenta
from app.services.venta_service import venta_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/ventas",
    service=venta_service,
    create_schema=CrearVenta,
    update_schema=ActualizarVenta,
    read_schema=RespuestaVenta,
    tag="Ventas",
    item_name="venta",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([1, 4]))],
    create_deps=[Depends(RoleChecker([1, 4]))],
    delete_deps=[Depends(RoleChecker([4]))],
    read_deps=[Depends(RoleChecker([1, 4]))],
    obtain_deps=[Depends(RoleChecker([1, 4]))]
)
