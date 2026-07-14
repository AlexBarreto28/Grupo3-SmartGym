from sqlalchemy import select, func, String, Integer, Float, Boolean, Date, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ReglaNegocioException
from datetime import datetime
from typing import Any
from sqlalchemy.orm import joinedload
from app.services.base_service import CRUDBase
from app.models.reserva import Reserva
from app.models.cliente import Cliente
from app.models.sesion_programada import SesionProgramada
from app.models.membresia_cliente import MembresiaCliente
from app.core.exceptions import ReglaNegocioException
from datetime import date

class CRUDReserva(CRUDBase[Reserva]):
    async def obtener_todos(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Reserva]:
        result = await db.execute(
            select(Reserva).options(joinedload(Reserva.cliente)).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def obtener_paginado(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, filters: dict | None = None) -> dict[str, Any]:
        return await super().obtener_paginado(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            options=[joinedload(Reserva.cliente)],
        )

    async def obtener(self, db: AsyncSession, id: Any) -> Reserva | None:
        result = await db.execute(
            select(Reserva)
            .where(Reserva.id == id)
            .options(joinedload(Reserva.cliente))
        )
        return result.scalars().first()
    
    async def verificar_solapamiento(self, db: AsyncSession, cliente_id: int, nueva_sesion: SesionProgramada):
        stmt = (
            select(SesionProgramada)
            .join(Reserva, Reserva.sesion_id == SesionProgramada.id)
            .where(
                Reserva.cliente_id == cliente_id,
                Reserva.estado == "activo",
                SesionProgramada.fecha == nueva_sesion.fecha,
                SesionProgramada.hora_inicio < nueva_sesion.hora_fin,
                SesionProgramada.hora_fin > nueva_sesion.hora_inicio
            )
        )
        
        result = await db.execute(stmt)
        clase_solapada = result.scalars().first()
        
        if clase_solapada:
            raise ReglaNegocioException(
                codigo_interno="ERR_RESERVA_SOLAPAMIENTO_HORARIO",
                mensaje="El cliente ya tiene una reserva en este bloque horario."
            )

    async def crear(self, db: AsyncSession, *, obj_in: dict) -> Reserva:
        from datetime import date
        
        cliente_id = obj_in.get("cliente_id")
        sesion_id = obj_in.get("sesion_id")
        
        if not cliente_id or not sesion_id:
            raise ReglaNegocioException(
                codigo_interno="ERR_PARAMETROS_REQUERIDOS",
                mensaje="Los campos 'cliente_id' y 'sesion_id' son obligatorios.",
                status_code=400,
            )
        
        
        stmt_membresia = select(MembresiaCliente).where(
            MembresiaCliente.cliente_id == cliente_id,
            MembresiaCliente.estado == "activo",
            MembresiaCliente.fecha_inicio <= date.today(),
            MembresiaCliente.fecha_vencimiento >= date.today()
        )
        result_membresia = await db.execute(stmt_membresia)
        membresia_activa = result_membresia.scalars().first()
        
        if not membresia_activa:
            raise ReglaNegocioException(
                codigo_interno="ERR_MEMBRESIA_INACTIVA",
                mensaje="El cliente no tiene una membresía activa para reservar clases."
            )
        
        stmt_sesion = select(SesionProgramada).where(SesionProgramada.id == sesion_id)
        result_sesion = await db.execute(stmt_sesion)
        nueva_sesion = result_sesion.scalars().first()
        
        if not nueva_sesion:
            raise ReglaNegocioException(
                codigo_interno="ERR_SESION_NO_ENCONTRADA",
                mensaje="La sesión de clase solicitada no existe."
            )
            
        if nueva_sesion.estado.lower() != "activo":
            raise ReglaNegocioException(
                codigo_interno="ERR_SESION_INACTIVA",
                mensaje="No se pueden realizar reservas para una clase que no esté activa."
            )

        stmt_duplicado = select(Reserva).where(
            Reserva.cliente_id == cliente_id,
            Reserva.sesion_id == sesion_id,
            Reserva.estado == "activo"
        )
        result_duplicado = await db.execute(stmt_duplicado)
        if result_duplicado.scalars().first():
            raise ReglaNegocioException(
                codigo_interno="ERR_RESERVA_DUPLICADA",
                mensaje="El cliente ya posee una reserva activa para esta clase exacta."
            )

        stmt_conteo = select(func.count(Reserva.id)).where(
            Reserva.sesion_id == sesion_id,
            Reserva.estado == "activo"
        )
        result_conteo = await db.execute(stmt_conteo)
        total_reservas = result_conteo.scalar() or 0

        if total_reservas >= nueva_sesion.cupo_maximo:
            raise ReglaNegocioException(
                codigo_interno="ERR_CLASE_LLENA",
                mensaje=f"La sesión ha alcanzado su límite máximo de {nueva_sesion.cupo_maximo} cupos."
            )

        await self.verificar_solapamiento(db, cliente_id=cliente_id, nueva_sesion=nueva_sesion)
        
        obj_in["fecha_reserva"] = datetime.now()
        obj_in["estado"] = "activo"
        
        nueva_reserva = Reserva(**obj_in)
        db.add(nueva_reserva)
        await self._commit(db)
        await db.refresh(nueva_reserva)
        
        return nueva_reserva

    async def cancelar_reserva(self, db: AsyncSession, reserva_id: int):
        return await self.eliminacion_logica(db, id=reserva_id)

reserva_service = CRUDReserva(Reserva) 