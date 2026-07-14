from fastapi import Depends
from fastapi.security import HTTPBearer
from app.core.exceptions import ReglaNegocioException
from app.core.security import decode_token


security_scheme = HTTPBearer()

class RoleChecker:
    def __init__(self, allowed_roles_ids: list[int]):
        self.allowed_roles_ids = allowed_roles_ids

    async def __call__(self, token: str = Depends(security_scheme)):
        payload = decode_token(token.credentials)
        print(payload)
        
        if not payload:
            raise ReglaNegocioException(
                codigo_interno="ERR_TOKEN_INVALIDO",
                mensaje="Token inválido o expirado",
                status_code=401,
            )
        user_role_id = payload.get("role_id")
        if user_role_id not in self.allowed_roles_ids:
            raise ReglaNegocioException(
                codigo_interno="ERR_SIN_PERMISOS",
                mensaje="No tienes los permisos necesarios para esta acción",
                status_code=403,
            )
        
        return payload