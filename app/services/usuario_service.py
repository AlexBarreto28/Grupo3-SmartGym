from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.exceptions import ReglaNegocioException
from typing import Any
from sqlalchemy.orm import joinedload
from app.services.base_service import CRUDBase
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.core.security import hash_password
from sqlalchemy.orm import selectinload
from sqlalchemy import func, String, Integer, Float, Boolean, Date, DateTime
from datetime import datetime, date

class CRUDUsuario(CRUDBase[Usuario]):

    async def obtener_todos(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Usuario]:
        result = await db.execute(
            select(Usuario).options(joinedload(Usuario.rol)).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def obtener(self, db: AsyncSession, id: Any) -> Usuario | None:
        result = await db.execute(
            select(Usuario)
            .where(Usuario.id == id)
            .options(joinedload(Usuario.rol))
        )
        return result.scalars().first()
    
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> Usuario:

        rol_id = obj_in.get("rol_id")
        result = await db.execute(select(Rol).filter(Rol.id == rol_id))
        rol = result.scalars().first()

        if not rol:
            raise ReglaNegocioException(
                codigo_interno="ERR_ROL_NO_EXISTE",
                mensaje="El rol especificado no existe.",
                status_code=404,
            )
    
        email = obj_in.get("email")
        result_email = await db.execute(select(Usuario).filter(Usuario.email == email))
        usuario_existente = result_email.scalars().first()

        if usuario_existente:
            raise ReglaNegocioException(
                codigo_interno="ERR_EMAIL_DUPLICADO",
                mensaje="Este correo electrónico ya está registrado en el sistema.",
                status_code=400,
            )

        obj_in["password"] = hash_password(obj_in["password"])

        nuevo_usuario = await super().crear(db, obj_in=obj_in)
        
        return await self.obtener(db, id=nuevo_usuario.id)

    async def obtener_paginado(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, filters: dict | None = None) -> dict[str, Any]:
        return await super().obtener_paginado(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            options=[joinedload(Usuario.rol)],
        )

usuario_service = CRUDUsuario(Usuario)
