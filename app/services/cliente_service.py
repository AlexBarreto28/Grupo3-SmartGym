from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.cliente import Cliente
from app.models.usuario import Usuario  
from app.services.base_service import CRUDBase
from typing import Any
from app.core.exceptions import ReglaNegocioException 
from datetime import date
from app.core.security import hash_password

class CRUDCliente(CRUDBase[Cliente]):
    
    async def buscar_por_nombre(self, db: AsyncSession, nombre: str) -> Cliente | None:
        result = await db.execute(
            select(Cliente).where(Cliente.nombre_completo == nombre)
        )
        return result.scalars().first()

    async def obtener_todos(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Cliente]:
        return await super().obtener_todos(db, skip=skip, limit=limit, options=[joinedload(Cliente.usuario)])

    async def obtener_paginado(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, filters: dict | None = None) -> dict[str, Any]:
        return await super().obtener_paginado(
            db, skip=skip, limit=limit, filters=filters, options=[joinedload(Cliente.usuario)]
        )

    async def obtener(self, db: AsyncSession, id: Any) -> Cliente | None:
        return await super().obtener(db, id=id, options=[joinedload(Cliente.usuario)])

    async def crear(self, db: AsyncSession, *, obj_in: dict) -> Cliente:
        cedula = obj_in.get("cedula")
        email = obj_in.get("email")

        stmt_cedula = select(Cliente).where(Cliente.cedula == cedula)
        result_cedula = await db.execute(stmt_cedula)
        cedula_existente = result_cedula.scalars().first()

        if cedula_existente:
            raise ReglaNegocioException(
                codigo_interno="ERR_CEDULA_DUPLICADA",
                mensaje=f"Ya existe un cliente registrado con la cédula {cedula}.",
                status_code=400,
            )
        
        stmt_usuario = select(Usuario).where(Usuario.email == email)
        result_usuario = await db.execute(stmt_usuario)
        usuario_existente = result_usuario.scalars().first()

        if usuario_existente:
            raise ReglaNegocioException(
                codigo_interno="ERR_EMAIL_DUPLICADO",
                mensaje="Este correo electrónico ya está registrado.",
                status_code=400,
            )

        try:

            usuario = Usuario(
                nombre=obj_in["nombre"],
                email=obj_in["email"],
                password=hash_password(obj_in["password"]),
                rol_id=3,
                estado="activo",
            )

            db.add(usuario)

            await db.flush()

            cliente = Cliente(
                cedula=obj_in["cedula"],
                telefono=obj_in.get("telefono"),
                fecha_registro=date.today(),
                usuario_id=usuario.id,
            )

            db.add(cliente)

            await db.commit()

            await db.refresh(cliente)

            return await self.obtener(db, cliente.id)

        except Exception:
            await db.rollback()
            raise

cliente_service = CRUDCliente(Cliente)