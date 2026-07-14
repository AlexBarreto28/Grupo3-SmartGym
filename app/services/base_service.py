from typing import Generic, Type, TypeVar, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, String, Integer, Float, Boolean, Date, DateTime
from sqlalchemy.exc import IntegrityError
from app.db.base import Base
from app.core.exceptions import ReglaNegocioException
from datetime import datetime, date

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def obtener(
        self, db: AsyncSession, id: Any, options: list | None = None
    ) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        if options:
            query = query.options(*options)
        result = await db.execute(query)
        return result.scalars().first()

    async def obtener_todos(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, options: list | None = None
    ) -> List[ModelType]:
        query = select(self.model)
        if options:
            query = query.options(*options)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def obtener_paginado(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 10,
        filters: dict | None = None,
        options: list | None = None
    ) -> dict[str, Any]:
        query = select(self.model)

        if options:
            query = query.options(*options)

        if filters:
            for field, value in filters.items():
                if not hasattr(self.model, field):
                    continue

                column = getattr(self.model, field)

                try:
                    column_type = column.property.columns[0].type

                    if isinstance(column_type, String):
                        query = query.where(column.ilike(f"%{value}%"))
                    elif isinstance(column_type, Integer):
                        query = query.where(column == int(value))
                    elif isinstance(column_type, Float):
                        query = query.where(column == float(value))
                    elif isinstance(column_type, Boolean):
                        query = query.where(column == (str(value).lower() == "true"))
                    elif isinstance(column_type, Date):
                        query = query.where(column == date.fromisoformat(value))
                    elif isinstance(column_type, DateTime):
                        query = query.where(column == datetime.fromisoformat(value))
                    else:
                        query = query.where(column == value)

                except (ValueError, TypeError, AttributeError):
                    continue

        total_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(total_query)

        result = await db.execute(query.offset(skip).limit(limit))

        return {"total": total, "items": result.scalars().all()}

    async def crear(self, db: AsyncSession, *, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as exc:
            await db.rollback()
            raise ReglaNegocioException(
                codigo_interno="ERR_INTEGRITY",
                mensaje="No se pudo crear el registro debido a un conflicto de datos.",
                status_code=400,
                error=str(exc)
            ) from exc

    async def actualizar(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: dict
    ) -> ModelType:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as exc:
            await db.rollback()
            raise ReglaNegocioException(
                codigo_interno="ERR_INTEGRITY",
                mensaje="No se pudo actualizar el registro debido a un conflicto de datos.",
                status_code=400,
                error=str(exc)
            ) from exc

    async def _commit(self, db: AsyncSession) -> None:
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ReglaNegocioException(
                codigo_interno="ERR_INTEGRITY",
                mensaje="Conflicto de datos en la base de datos.",
                status_code=400,
                error=str(exc),
            ) from exc

    async def cambiar_estado(
        self, db: AsyncSession, *, id: Any, estado: str
    ) -> Optional[ModelType]:
        obj = await db.get(self.model, id)
        if obj and hasattr(obj, "estado"):
            obj.estado = estado
            await db.commit()
            await db.refresh(obj)
            return obj
        return None


    async def eliminacion_logica(
        self, db: AsyncSession, *, id: int
    ) -> Optional[ModelType]:
        obj = await db.get(self.model, id)
        if obj and hasattr(obj, "estado"):
            obj.estado = "inactivo"
            await db.commit()
            await db.refresh(obj)
        return obj

    async def activar(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        obj = await db.get(self.model, id)
        if obj and hasattr(obj, "estado") and getattr(obj, "estado") == "inactivo":
            obj.estado = "activo"
            await db.commit()
            await db.refresh(obj)
            return obj
        return None

    async def eliminacion_fisica(self, db: AsyncSession, *, id: int) -> bool:
        obj = await db.get(self.model, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False
