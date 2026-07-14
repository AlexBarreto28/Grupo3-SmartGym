# app/api/v1/endpoints/auth_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import auth_service
from app.core.exceptions import ReglaNegocioException
from app.schemas.login import LoginRequest

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    token = await auth_service.autencicar_usuario(
        db=db,
        email=login_data.email,
        password_plana=login_data.password
    )
    return {
        "access_token": token,
        "token_type": "bearer"
    }