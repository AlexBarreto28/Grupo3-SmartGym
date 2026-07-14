from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usuario import Usuario
from app.core.security import verify_password, create_access_token
from app.core.exceptions import ReglaNegocioException

class AuthService:
    async def autencicar_usuario(self, db: AsyncSession, email: str, password_plana: str) -> str:

        result = await db.execute(select(Usuario).where(Usuario.email == email))
        usuario = result.scalars().first()

        if not usuario or not verify_password(password_plana, usuario.password):
            raise ReglaNegocioException(
                codigo_interno="ERR_AUTH_INVALID_CREDENTIALS",
                mensaje="Usuario o contraseña incorrectos"
            )
        if hasattr(usuario, "estado") and usuario.estado != "activo":
            raise ReglaNegocioException(
                codigo_interno="ERR_AUTH_INACTIVE_USER",
                mensaje="El usuario se encuentra inactivo"
            )

        access_token = create_access_token(
            data={"sub": str(usuario.id), "role_id": usuario.rol_id}
        )
        return access_token

auth_service = AuthService()