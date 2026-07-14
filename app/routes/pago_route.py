from app.routes.crud_router import create_crud_router
from app.schemas.pago import CrearPago, ActualizarPago, RespuestaPago
from app.services.pago_service import pago_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/pagos",
    service=pago_service,
    create_schema=CrearPago,
    update_schema=ActualizarPago,
    read_schema=RespuestaPago,
    tag="Pagos",
    item_name="pago",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([4]))],
    create_deps=[Depends(RoleChecker([4, 3]))],
    delete_deps=[Depends(RoleChecker([4]))],
    read_deps=[Depends(RoleChecker([4, 1]))],
    obtain_deps=[Depends(RoleChecker([4, 1]))]
)
