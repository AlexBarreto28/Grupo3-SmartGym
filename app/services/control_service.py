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
        cedula = obj_in.get("cedula")

        if not cedula:
            raise ReglaNegocioException(
                codigo_interno="ERR_CAMPO_REQUERIDO",
                mensaje="El campo 'cedula' es obligatorio.",
                status_code=400,
            )

        stmt_cliente = select(Cliente).where(Cliente.cedula == cedula)
        result_cliente = await db.execute(stmt_cliente)
        cliente = result_cliente.scalars().first()

        if not cliente:
            raise ReglaNegocioException(
                codigo_interno="ERR_CLIENTE_NO_ENCONTRADO",
                mensaje="No existe un cliente con la cédula indicada.",
                status_code=404,
            )

        hoy = date.today()

        stmt = (
            select(MembresiaCliente)
            .where(
                MembresiaCliente.cliente_id == cliente.id,
                MembresiaCliente.estado == "activo",
                MembresiaCliente.fecha_vencimiento >= hoy,
            )
            .order_by(MembresiaCliente.fecha_vencimiento.desc())
        )

        result = await db.execute(stmt)
        membresia = result.scalars().first()

        if not membresia:
            raise ReglaNegocioException(
                codigo_interno="ERR_MEMBRESIA_NO_ENCONTRADA",
                mensaje="Acceso denegado: El cliente no posee ninguna membresía activa y vigente.",
                status_code=403,
            )

        db_obj = ControlAcceso(
            cliente_id=cliente.id,
            mensaje=f"Acceso permitido - Membresía válida hasta {membresia.fecha_vencimiento}",
            estado="activo",
        )

        db.add(db_obj)
        await self._commit(db)
        await db.refresh(db_obj)

        return db_obj

control_acceso_service = CRUDControlAcceso(ControlAcceso)
