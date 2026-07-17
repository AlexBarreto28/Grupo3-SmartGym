from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.venta_tienda import VentaTienda
from app.models.producto_tienda import ProductoTienda
from app.services.base_service import CRUDBase
from app.services.venta_detalle_service import detalle_venta_service
from app.core.exceptions import ReglaNegocioException


class CRUDVenta(CRUDBase[VentaTienda]):
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> VentaTienda:

        detalles_lista = obj_in.pop("detalles", [])

        total = 0

        for detalle in detalles_lista:
            producto = await db.execute(
                select(ProductoTienda).where(
                    ProductoTienda.id == detalle["producto_id"]
                )
            )

            producto = producto.scalars().first()

            if not producto:
                raise ReglaNegocioException(
                    codigo_interno="ERR_PRODUCTO_NO_ENCONTRADO",
                    mensaje=f"El producto con ID {detalle['producto_id']} no existe.",
                )

            total += producto.precio * detalle["cantidad"]

        nueva_venta = VentaTienda(cliente_id=obj_in["cliente_id"], total=total)

        db.add(nueva_venta)

        await db.flush()

        for detalle in detalles_lista:
            detalle["venta_id"] = nueva_venta.id

            await detalle_venta_service.crear(db, obj_in=detalle)

        await self._commit(db)

        await db.refresh(nueva_venta)

        return nueva_venta


venta_service = CRUDVenta(VentaTienda)
