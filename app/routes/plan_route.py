from app.routes.crud_router import create_crud_router
from app.schemas.plan_suscripcion import CrearPlan, ActualizarPlan, RespuestaPlan
from app.services.plan_service import plan
from fastapi import Depends
from app.core.deps import RoleChecker

router = create_crud_router(
    prefix="/api/v1/planes",
    service=plan,
    create_schema=CrearPlan,
    update_schema=ActualizarPlan,
    read_schema=RespuestaPlan,
    tag="Planes",
    item_name="plan",
    activate=True,
    update_deps=[Depends(RoleChecker([1]))],
    create_deps=[Depends(RoleChecker([1]))],
    delete_deps=[Depends(RoleChecker([1]))],
    read_deps=[Depends(RoleChecker([1]))],
    obtain_deps=[Depends(RoleChecker([1]))]
)
