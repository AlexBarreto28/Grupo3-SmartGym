from app.routes.crud_router import create_crud_router
from app.schemas.reserva import CrearReserva, ActualizarReserva, RespuestaReserva
from app.services.reserva_service import reserva_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/reservas",
    service=reserva_service,
    create_schema=CrearReserva,
    update_schema=ActualizarReserva,
    read_schema=RespuestaReserva,
    tag="Reservas",
    item_name="reserva",
    activate=True,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([1, 2]))],
    create_deps=[Depends(RoleChecker([1, 2, 3]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1, 2, 3]))],
    obtain_deps=[Depends(RoleChecker([1, 2, 3]))]
)
