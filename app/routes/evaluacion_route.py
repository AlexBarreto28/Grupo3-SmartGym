from app.routes.crud_router import create_crud_router
from app.schemas.evaluacion_biometrica import CrearEvaluacion, ActualizarEvaluacion, RespuestaEvaluacion
from app.services.evaluacion_service import evaluacion_service
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/evaluaciones_biometricas",
    service=evaluacion_service,
    create_schema=CrearEvaluacion,
    update_schema=ActualizarEvaluacion,
    read_schema=RespuestaEvaluacion,
    tag="Evaluaciones Biometricas",
    item_name="evaluacion biometrica",
    activate=True,
    allow_update=False,
    allow_delete=False,
    update_deps=[Depends(RoleChecker([2]))],
    create_deps=[Depends(RoleChecker([2]))],
    delete_deps=[Depends(RoleChecker([2]))],
    read_deps=[Depends(RoleChecker([1, 2]))],
    obtain_deps=[Depends(RoleChecker([1, 2]))]
)
