from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.venta_tienda import VentaTienda
from app.models.producto_tienda import ProductoTienda
from app.models.cliente import Cliente  # ✅ AGREGAR: import
from app.services.base_service import CRUDBase
from app.services.venta_detalle_service import detalle_venta_service
from app.core.exceptions import ReglaNegocioException


class CRUDVenta(CRUDBase[VentaTienda]):
    async def crear(self, db: AsyncSession, *, obj_in: dict) -> VentaTienda:
        
        # 1. OBTENER Y VALIDAR CLIENTE
        cliente_id = obj_in.get("cliente_id")
        
        if not cliente_id:
            raise ReglaNegocioException(
                codigo_interno="ERR_CLIENTE_REQUERIDO",
                mensaje="El campo 'cliente_id' es obligatorio para registrar una venta.",
                status_code=400,
            )
        
        # VALIDAR QUE EL CLIENTE EXISTE
        cliente_result = await db.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        cliente = cliente_result.scalars().first()
        
        if not cliente:
            raise ReglaNegocioException(
                codigo_interno="ERR_CLIENTE_NO_EXISTE",
                mensaje=f"El cliente con ID {cliente_id} no existe.",
                status_code=404,
            )
        
        # 2. OBTENER DETALLES DE LA VENTA
        detalles_lista = obj_in.pop("detalles", [])
        
        if not detalles_lista:
            raise ReglaNegocioException(
                codigo_interno="ERR_DETALLES_REQUERIDOS",
                mensaje="La venta debe tener al menos un detalle.",
                status_code=400,
            )
        
        # 3. VALIDAR PRODUCTOS Y CALCULAR TOTAL
        total = 0
        productos_validados = []
        
        for detalle in detalles_lista:
            producto_id = detalle.get("producto_id")
            cantidad = detalle.get("cantidad", 0)
            
            # Validar cantidad
            if cantidad <= 0:
                raise ReglaNegocioException(
                    codigo_interno="ERR_CANTIDAD_INVALIDA",
                    mensaje=f"La cantidad para el producto ID {producto_id} debe ser mayor a 0.",
                    status_code=400,
                )
            
            # VALIDAR QUE EL PRODUCTO EXISTE
            producto_result = await db.execute(
                select(ProductoTienda).where(ProductoTienda.id == producto_id)
            )
            producto = producto_result.scalars().first()
            
            if not producto:
                raise ReglaNegocioException(
                    codigo_interno="ERR_PRODUCTO_NO_ENCONTRADO",
                    mensaje=f"El producto con ID {producto_id} no existe.",
                    status_code=404,
                )
            
            # VALIDAR QUE HAYA STOCK SUFICIENTE
            if producto.stock < cantidad:
                raise ReglaNegocioException(
                    codigo_interno="ERR_STOCK_INSUFICIENTE",
                    mensaje=f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}, Solicitado: {cantidad}",
                    status_code=409,
                )
            
            # Calcular subtotal
            subtotal = float(producto.precio) * cantidad
            total += subtotal
            
            # Guardar producto validado para después
            productos_validados.append({
                "producto": producto,
                "cantidad": cantidad,
                "detalle": detalle
            })
        
        # 4. CREAR LA VENTA
        nueva_venta = VentaTienda(
            cliente_id=cliente_id,
            total=total
        )
        
        db.add(nueva_venta)
        await db.flush()  # Para obtener el ID de la venta
        
        # 5. CREAR DETALLES Y ACTUALIZAR STOCK
        for item in productos_validados:
            producto = item["producto"]
            cantidad = item["cantidad"]
            detalle = item["detalle"]
            
            # Crear el detalle
            detalle["venta_id"] = nueva_venta.id
            await detalle_venta_service.crear(db, obj_in=detalle)
            
            # Actualizar stock del producto
            producto.stock -= cantidad
        
        # 6. CONFIRMAR TRANSACCIÓN
        await db.commit()
        await db.refresh(nueva_venta)
        
        return nueva_venta


venta_service = CRUDVenta(VentaTienda)