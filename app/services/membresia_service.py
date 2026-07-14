from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import CRUDBase
from app.models.membresia_cliente import MembresiaCliente
from app.models.plan_suscripcion import PlanSuscripcion
from app.models.cliente import Cliente
from app.core.exceptions import ReglaNegocioException
from datetime import date

class CRUDMembresia(CRUDBase[MembresiaCliente]):
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> MembresiaCliente:

        fecha_inicio = obj_in.get("fecha_inicio")
        fecha_vencimiento = obj_in.get("fecha_vencimiento")

        if fecha_inicio and fecha_vencimiento and fecha_inicio == fecha_vencimiento:
            raise ReglaNegocioException(
                codigo_interno="ERR_FECHAS_INVALIDAS",
                mensaje="La fecha de inicio no puede ser igual a la fecha de vencimiento."
            )           

        plan_id = obj_in.get("plan_id")
        result_plan = await db.execute(
            select(PlanSuscripcion).where(PlanSuscripcion.id == plan_id)
        )

        plan = result_plan.scalars().first()
        if not plan:
            raise ReglaNegocioException(
                codigo_interno="ERR_PLAN_NO_EXISTE",
                mensaje="El plan de suscripción no existe."
            )      

        cliente_id = obj_in.get("cliente_id")

        result_cliente = await db.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        cliente = result_cliente.scalars().first()

        if not cliente:
            raise ReglaNegocioException(
                codigo_interno="ERR_CLIENTE_NO_EXISTE",
                mensaje="El cliente con el ID proporcionado no existe."
            )

        hoy = date.today()
        result_m = await db.execute(
            select(MembresiaCliente).where(
                MembresiaCliente.cliente_id == cliente_id,
                MembresiaCliente.estado.ilike("activa"),
                MembresiaCliente.fecha_vencimiento >= hoy,
            )
        )
        membresia_activa = result_m.scalars().first()
        if membresia_activa:
            raise ReglaNegocioException(
                codigo_interno="ERR_MEMB_EXISTENTE",
                mensaje="El cliente ya posee una membresía activa y vigente."
            )

        return await super().crear(db, obj_in=obj_in)

membresia_service = CRUDMembresia(MembresiaCliente)
