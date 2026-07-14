from typing import Any, Type, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, params, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.exceptions import ReglaNegocioException
import math


def create_crud_router(
    prefix: str,
    service: Any,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    read_schema: Type[BaseModel],
    tag: str,
    item_name: str = "item",
    state_schema: Optional[Type[BaseModel]] = None,
    activate: bool = False,
    create_deps: Optional[list[params.Depends]] = None,
    update_deps: Optional[list[params.Depends]] = None,
    delete_deps: Optional[list[params.Depends]] = None,
    read_deps: Optional[list[params.Depends]] = None,
    obtain_deps: Optional[list[params.Depends]] = None,
    allow_update: bool = True,
    allow_delete: bool = True,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("/", dependencies=read_deps)
    async def leer_varios(
        request: Request,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
    ):
        skip = (page - 1) * size

        filters = dict(request.query_params)

        filters.pop("page", None)
        filters.pop("size", None)

        data = await service.obtener_paginado(
            db,
            skip=skip,
            limit=size,
            filters=filters
        )

        return {
            "page": page,
            "size": size,
            "total": data["total"],
            "pages": math.ceil(data["total"] / size),
            "items": [
                read_schema.model_validate(item)
                for item in data["items"]
            ]
        }

    @router.get("/{item_id}", response_model=read_schema, dependencies=obtain_deps)
    async def leer(item_id: int, db: AsyncSession = Depends(get_db)):
        item = await service.obtener(db, item_id)
        if not item:
            raise ReglaNegocioException(
                codigo_interno="ERR_ITEM_NO_ENCONTRADO",
                mensaje=f"{item_name.capitalize()} no encontrado",
                status_code=404,
            )
        return item

    @router.post("/", response_model=read_schema, dependencies=create_deps, status_code=status.HTTP_201_CREATED)
    async def crear(obj_in: create_schema, db: AsyncSession = Depends(get_db)):
        return await service.crear(db, obj_in=obj_in.model_dump(exclude_none=True))

    if allow_update:

        @router.put("/{item_id}", response_model=read_schema, dependencies=update_deps)
        async def actualizar(
            item_id: int, obj_in: update_schema, db: AsyncSession = Depends(get_db)
        ):
            item = await service.obtener(db, item_id)

            if not item:
                raise ReglaNegocioException(
                    codigo_interno="ERR_ITEM_NO_ENCONTRADO",
                    mensaje=f"{item_name.capitalize()} no encontrado",
                    status_code=404,
                )

            return await service.actualizar(
                db, db_obj=item, obj_in=obj_in.model_dump(exclude_none=True)
            )

    if state_schema is not None:

        @router.put(
            "/{item_id}/estado", response_model=read_schema, dependencies=update_deps
        )
        async def cambiar_estado(
            item_id: int, obj_in: state_schema, db: AsyncSession = Depends(get_db)
        ):
            item = await service.cambiar_estado(db, id=item_id, estado=obj_in.estado)
            if not item:
                raise ReglaNegocioException(
                    codigo_interno="ERR_ITEM_NO_ENCONTRADO",
                    mensaje=f"{item_name.capitalize()} no encontrado o no tiene campo estado",
                    status_code=404,
                )
            return item

    if activate:

        @router.put(
            "/{item_id}/activar", response_model=read_schema, dependencies=update_deps
        )
        async def activar(item_id: int, db: AsyncSession = Depends(get_db)):
            item = await service.activar(db, id=item_id)
            if not item:
                raise ReglaNegocioException(
                    codigo_interno="ERR_ACTIVACION_FALLIDA",
                    mensaje=f"No se pudo activar el {item_name}. Verifique que exista y esté en estado inactivo.",
                    status_code=409,
                )
            return item

    if allow_delete:

        @router.delete("/{item_id}", dependencies=delete_deps, status_code=status.HTTP_204_NO_CONTENT)
        async def eliminar(item_id: int, db: AsyncSession = Depends(get_db)):
            deleted = await service.eliminacion_fisica(db, id=item_id)

            if not deleted:
                raise ReglaNegocioException(
                    codigo_interno="ERR_ITEM_NO_ENCONTRADO",
                    mensaje=f"{item_name.capitalize()} no encontrado",
                    status_code=404,
                )

            return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.put("/{item_id}/desactivar", dependencies=update_deps, status_code=status.HTTP_204_NO_CONTENT)
    async def desactivar(item_id: int, db: AsyncSession = Depends(get_db)):
        obj = await service.eliminacion_logica(db, id=item_id)
        if not obj:
            raise ReglaNegocioException(
                codigo_interno="ERR_ITEM_NO_ENCONTRADO",
                mensaje=f"{item_name.capitalize()} no encontrado",
                status_code=404,
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router