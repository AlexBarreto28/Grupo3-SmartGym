from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ReglaNegocioException
from app.services.base_service import CRUDBase
from app.models.control_acceso import ControlAcceso
from app.models.cliente import Cliente
from app.schemas.control_acceso import CrearControlAcceso
from app.models.membresia_cliente import MembresiaCliente
from datetime import date

class CRUDControlAcceso(CRUDBase[ControlAcceso]):
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> ControlAcceso:
        cliente_id = obj_in.get("cliente_id")

        if not cliente_id:
            raise ReglaNegocioException(
                codigo_interno="ERR_CAMPO_REQUERIDO",
                mensaje="El campo 'cliente_id' es obligatorio.",
                status_code=400,
            )
        hoy = date.today()

        stmt = (
            select(MembresiaCliente)
            .where(
                MembresiaCliente.cliente_id == cliente_id,
                MembresiaCliente.estado.ilike("activa"),
                MembresiaCliente.fecha_vencimiento >= hoy,
            )
            .order_by(MembresiaCliente.fecha_vencimiento.desc())
        )
        result = await db.execute(stmt)
        membresia = result.scalars().first()

        if not membresia:
            raise ReglaNegocioException(
                codigo_interno="ERR_MEMBRESIA_NO_ENCONTRADA",
                mensaje=f"Acceso denegado: El cliente no posee ninguna membresía activa y vigente."
            )

        db_obj = ControlAcceso(
            cliente_id=cliente_id,
            mensaje=f"Acceso permitido - Membresía válida hasta {membresia.fecha_vencimiento}",
            estado="activo"
        )
        
        db.add(db_obj)
        await self._commit(db)
        await db.refresh(db_obj)
        
        return db_obj

control_acceso_service = CRUDControlAcceso(ControlAcceso)
