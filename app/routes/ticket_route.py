from app.routes.crud_router import create_crud_router
from app.schemas.ticket_mantenimiento import CrearTicket, ActualizarTicket, RespuestaTicket
from app.services.ticket_service import ticket_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/tickets_mantenimiento",
    service=ticket_service,
    create_schema=CrearTicket,
    update_schema=ActualizarTicket,
    read_schema=RespuestaTicket,
    tag="Tickets Mantenimiento",
    item_name="ticket",
    activate=True,
    update_deps=[Depends(RoleChecker([1, 2]))],
    create_deps=[Depends(RoleChecker([1, 2]))],
    delete_deps=[Depends(RoleChecker([1, 2]))],
    read_deps=[Depends(RoleChecker([1, 2]))],
    obtain_deps=[Depends(RoleChecker([1, 2]))]
)
