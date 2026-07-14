from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ReglaNegocioException
from app.services.base_service import CRUDBase
from app.models.pago import Pago
from app.models.usuario import Usuario
from app.models.membresia_cliente import MembresiaCliente

class CRUDPago(CRUDBase[Pago]):
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> Pago:

        usuario_id = obj_in.get("usuario_id")
        usuario = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
        usuario = usuario.scalars().first()

        if not usuario:
            raise ReglaNegocioException(
                    codigo_interno="ERR_ID_INVALIDO",
                    mensaje=f"Usuario no encontrado con el ID '{usuario_id}'."
                )
            
        membresia = await db.execute(
            select(MembresiaCliente).where(MembresiaCliente.cliente_id == usuario.id)
        )
        membresia = membresia.scalars().first()

        if not membresia:
            raise ReglaNegocioException(
                    codigo_interno="ERR_MEMBRESIA_NO_EXISTE",
                    mensaje=f"Membresía no encontrada para el usuario con ID '{usuario_id}'."
                )
        obj_in["membresia_id"] = membresia.id

        pago = await super().crear(db, obj_in=obj_in)

        membresia.estado = "activo"
        await self._commit(db)

        return pago


    async def actualizar(self, db: AsyncSession, *, db_obj: Pago, obj_in: dict) -> Pago:
        raise ReglaNegocioException(
            codigo_interno="ERR_PAGO_INMUTABLE",
            mensaje="No se puede modificar un pago después de creado. Los pagos son inmutables.",
            status_code=405,
        )
    
   
    async def eliminacion_fisica(self, db: AsyncSession, *, id: int) -> bool:
        raise ReglaNegocioException(
            codigo_interno="ERR_PAGO_INMUTABLE",
            mensaje="No se puede eliminar un pago. Los pagos son inmutables.",
            status_code=405,
        )


pago_service = CRUDPago(Pago)