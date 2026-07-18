from sqlalchemy import select, func, String, Integer, Float, Boolean, Date, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ReglaNegocioException
from app.services.base_service import CRUDBase
from app.models.sesion_programada import SesionProgramada
from app.models.entrenador import Entrenador
from app.models.disciplina import Disciplina
from typing import Any
from sqlalchemy.orm import joinedload
from datetime import datetime, date

class CRUDSesion(CRUDBase[SesionProgramada]):
    async def obtener_por_entrenador(self, db: AsyncSession, entrenador_id: int):
        result = await db.execute(
            select(SesionProgramada).where(
                SesionProgramada.entrenador_id == entrenador_id,
                SesionProgramada.estado == "activo",
            )
        )
        return result.scalars().all()

    async def obtener_todos(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[SesionProgramada]:
        result = await db.execute(
            select(SesionProgramada).options(joinedload(SesionProgramada.entrenador)).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def obtener_paginado(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, filters: dict | None = None) -> dict[str, Any]:
        return await super().obtener_paginado(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            options=[joinedload(SesionProgramada.entrenador)],
        )


    async def obtener(self, db: AsyncSession, id: Any) -> SesionProgramada | None:
        result = await db.execute(
            select(SesionProgramada)
            .where(SesionProgramada.id == id)
            .options(joinedload(SesionProgramada.entrenador))
        )
        return result.scalars().first()

    async def crear(self, db: AsyncSession, *, obj_in: dict) -> SesionProgramada:
        hora_inicio = obj_in.get("hora_inicio")
        hora_fin = obj_in.get("hora_fin")
        cupos = obj_in.get("cupos")
        entrenador_id = obj_in.get("entrenador_id")
        fecha = obj_in.get("fecha")

        if hora_inicio and hora_fin and hora_inicio == hora_fin:
            raise ReglaNegocioException(
                codigo_interno="ERR_HORAS_INVALIDAS",
                mensaje="La hora de inicio no puede ser idéntica a la hora de finalización.",
                status_code=400,
            )

        if cupos is not None and cupos <= 0:
            raise ReglaNegocioException(
                codigo_interno="ERR_CUPOS_INVALIDOS",
                mensaje="La cantidad de cupos debe ser un número estrictamente mayor a cero.",
                status_code=400,
            )

        entrenador = await db.execute(
            select(Entrenador).where(Entrenador.id == entrenador_id)
        )
        entrenador = entrenador.scalars().first()

        if not entrenador:
            raise ReglaNegocioException(
                codigo_interno="ERR_ENTRENADOR_NO_EXISTE",
                mensaje="El entrenador no existe.",
                status_code=404,
            )

        disciplina_id = obj_in.get("disciplina_id")

        disciplina = await db.execute(
            select(Disciplina).where(Disciplina.id == disciplina_id)
        )
        disciplina = disciplina.scalars().first()

        if not disciplina:
            raise ReglaNegocioException(
                codigo_interno="ERR_DISCIPLINA_NO_EXISTE",
                mensaje="La disciplina no existe.",
                status_code=404,
            )

        if hora_inicio and hora_fin and entrenador_id:
            stmt_solapamiento = select(SesionProgramada).where(
                SesionProgramada.entrenador_id == entrenador_id,
                SesionProgramada.estado == "activo",
                SesionProgramada.fecha == fecha,
                SesionProgramada.hora_inicio < hora_fin,
                SesionProgramada.hora_fin > hora_inicio
            )
            
            result_solapamiento = await db.execute(stmt_solapamiento)
            sesion_conflictiva = result_solapamiento.scalars().first()

            if sesion_conflictiva:
                raise ReglaNegocioException(
                    codigo_interno="ERR_SESION_SOLAPADA",
                    mensaje=f"El entrenador ya tiene una sesión activa programada en ese rango de horario.",
                    status_code=400,
                )

        return await super().crear(db, obj_in=obj_in)

sesion_service = CRUDSesion(SesionProgramada)