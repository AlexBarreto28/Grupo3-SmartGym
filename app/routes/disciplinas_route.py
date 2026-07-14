from app.routes.crud_router import create_crud_router
from app.schemas.disciplina import CrearDisciplina, ActualizarDisciplina, RespuestaDisciplina
from app.services.disciplinas_service import disciplina_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/disciplinas",
    service=disciplina_service,
    create_schema=CrearDisciplina,
    update_schema=ActualizarDisciplina,
    read_schema=RespuestaDisciplina,
    tag="Disciplinas",
    item_name="disciplina",
    activate=True,
    update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1, 2]))],
    obtain_deps=[Depends(RoleChecker([1, 2]))]
)
