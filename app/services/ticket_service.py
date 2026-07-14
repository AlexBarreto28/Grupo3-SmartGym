from datetime import datetime
from sqlalchemy import select, func, String, Integer, Float, Boolean, Date, DateTime
from typing import Any
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ReglaNegocioException
from app.services.base_service import CRUDBase
from app.models.ticket_mantenimiento import TicketMantenimiento
from app.models.usuario import Usuario
from app.models.maquina import Maquina
from datetime import date

class CRUDTicketMantenimiento(CRUDBase[TicketMantenimiento]):
    async def obtener_todos(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[TicketMantenimiento]:
        result = await db.execute(
            select(TicketMantenimiento).options(joinedload(TicketMantenimiento.maquina)).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def obtener_paginado(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, filters: dict | None = None) -> dict[str, Any]:
        return await super().obtener_paginado(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            options=[joinedload(TicketMantenimiento.maquina)],
        )


    async def obtener(self, db: AsyncSession, id: Any) -> TicketMantenimiento | None:
        result = await db.execute(
            select(TicketMantenimiento)
            .where(TicketMantenimiento.id == id)
            .options(joinedload(TicketMantenimiento.maquina))
        )
        return result.scalars().first()

    async def crear(self, db: AsyncSession, *, obj_in: dict) -> TicketMantenimiento:
        usuario_id = obj_in.get("usuario_id")
        usuario = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
        usuario = usuario.scalars().first()
        if not usuario:
            raise ReglaNegocioException(
                codigo_interno="ERR_USUARIO_NO_EXISTE",
                mensaje="El usuario no existe.",
                status_code=404,
            )
        maquina_id = obj_in.get("maquina_id")
        maquina = await db.execute(select(Maquina).where(Maquina.id == maquina_id))
        maquina = maquina.scalars().first()
        if not maquina:
            raise ReglaNegocioException(
                codigo_interno="ERR_MAQUINA_NO_EXISTE",
                mensaje="La máquina no existe.",
                status_code=404,
            )

        if maquina.estado == "mantenimiento":
            raise ReglaNegocioException(
                codigo_interno="ERR_MAQUINA_MANTENIMIENTO",
                mensaje="La máquina ya se encuentra en mantenimiento.",
                status_code=409,
            )

        maquina.estado = "mantenimiento"
        db.add(maquina)
        return await super().crear(db, obj_in=obj_in)

    async def cerrar_ticket(
        self, db: AsyncSession, *, ticket_id: int, costo: float
    ) -> TicketMantenimiento:

        ticket = await db.get(TicketMantenimiento, ticket_id)

        if not ticket:
            raise ReglaNegocioException(
                codigo_interno="ERR_TICKET_NO_EXISTE",
                mensaje="El ticket no existe.",
                status_code=404,
            )

        if ticket.fecha_cierre:
            raise ReglaNegocioException(
                codigo_interno="ERR_TICKET_CERRADO",
                mensaje="El ticket ya fue cerrado.",
                status_code=409,
            )

        if costo < 0:
            raise ReglaNegocioException(
                codigo_interno="ERR_COSTO_INVALIDO",
                mensaje="El costo no puede ser negativo.",
                status_code=400,
            )
        ticket.costo = costo
        ticket.fecha_cierre = datetime.now()
        maquina = ticket.maquina
        maquina.estado = "activa"
        db.add(maquina)
        await self._commit(db)
        await db.refresh(ticket)
        return ticket

ticket_service = CRUDTicketMantenimiento(TicketMantenimiento)
