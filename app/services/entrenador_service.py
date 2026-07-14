from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import CRUDBase
from app.models.entrenador import Entrenador
from app.models.usuario import Usuario 
from app.core.exceptions import ReglaNegocioException  
from typing import Any

class CRUDEntrenador(CRUDBase[Entrenador]):
    async def buscar_por_especialidad(
        self, db: AsyncSession, especialidad: str
    ) -> Entrenador | None:
        result = await db.execute(
            select(Entrenador).where(Entrenador.especialidad == especialidad)
        )
        return result.scalars().first()
    
    async def obtener_todos(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Entrenador]:
        return await super().obtener_todos(db, skip=skip, limit=limit, options=[joinedload(Entrenador.usuario)])

    async def obtener_paginado(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, filters: dict | None = None) -> dict[str, Any]:
        return await super().obtener_paginado(
            db, skip=skip, limit=limit, filters=filters, options=[joinedload(Entrenador.usuario)]
        )

    async def obtener(self, db: AsyncSession, id: Any) -> Entrenador | None:
        return await super().obtener(db, id=id, options=[joinedload(Entrenador.usuario)])

    async def crear(self, db: AsyncSession, *, obj_in: dict) -> Entrenador:
        usuario_id = obj_in.get("usuario_id")

        if usuario_id:
            stmt_usuario = select(Usuario).where(Usuario.id == usuario_id)
            result_usuario = await db.execute(stmt_usuario)
            usuario_existente = result_usuario.scalars().first()

            if not usuario_existente:
                raise ReglaNegocioException(
                    codigo_interno="ERR_USUARIO_NO_ENCONTRADO",
                    mensaje=f"No se puede registrar el entrenador: El usuario con ID {usuario_id} no existe."
                )
        else:
            raise ReglaNegocioException(
                codigo_interno="ERR_USUARIO_REQUERIDO",
                mensaje="El campo 'usuario_id' es obligatorio para registrar un entrenador."
            )

        return await super().crear(db, obj_in=obj_in)

entrenador_service = CRUDEntrenador(Entrenador)