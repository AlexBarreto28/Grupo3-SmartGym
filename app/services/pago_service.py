from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ReglaNegocioException
from app.services.base_service import CRUDBase
from app.models.pago import Pago
from app.models.membresia_cliente import MembresiaCliente

class CRUDPago(CRUDBase[Pago]):
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> Pago:
        """
        Crea un nuevo pago.
        obj_in debe contener: membresia_id, monto, metodo_pago, current_user_id
        """
        
        # 1. Obtener current_user_id del obj_in
        current_user_id = obj_in.get("current_user_id")
        
        if not current_user_id:
            raise ReglaNegocioException(
                codigo_interno="ERR_USUARIO_REQUERIDO",
                mensaje="Se requiere el ID del usuario autenticado",
                status_code=400,
            )
        
        # 2. Obtener membresia_id del obj_in
        membresia_id = obj_in.get("membresia_id")
        
        if not membresia_id:
            raise ReglaNegocioException(
                codigo_interno="ERR_MEMBRESIA_REQUERIDA",
                mensaje="El campo 'membresia_id' es obligatorio",
                status_code=400,
            )
        
        # 3. BUSCAR MEMBRESIA POR ID
        result = await db.execute(
            select(MembresiaCliente).where(MembresiaCliente.id == membresia_id)
        )
        membresia = result.scalars().first()

        if not membresia:
            raise ReglaNegocioException(
                codigo_interno="ERR_MEMBRESIA_NO_EXISTE",
                mensaje=f"No se encontró una membresía con el ID '{membresia_id}'.",
                status_code=404,
            )
        
        # 4. ASIGNAR usuario_id (desde el token)
        obj_in["usuario_id"] = current_user_id
        
        # 5. Eliminar current_user_id del obj_in 
        obj_in.pop("current_user_id", None)
        
        # 6. CREAR EL PAGO usando el método base
        pago = await super().crear(db, obj_in=obj_in)
        
        # 7. ACTUALIZAR ESTADO DE LA MEMBRESIA A "activo"
        membresia.estado = "activo"
        await db.commit()
        
        return pago

    async def actualizar(self, db: AsyncSession, *, db_obj: Pago, obj_in: dict) -> Pago:
        """Los pagos son inmutables - no se pueden actualizar"""
        raise ReglaNegocioException(
            codigo_interno="ERR_PAGO_INMUTABLE",
            mensaje="No se puede modificar un pago después de creado. Los pagos son inmutables.",
            status_code=405,
        )
    
    async def eliminacion_fisica(self, db: AsyncSession, *, id: int) -> bool:
        """Los pagos son inmutables - no se pueden eliminar"""
        raise ReglaNegocioException(
            codigo_interno="ERR_PAGO_INMUTABLE",
            mensaje="No se puede eliminar un pago. Los pagos son inmutables.",
            status_code=405,
        )

pago_service = CRUDPago(Pago)

