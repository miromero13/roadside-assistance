from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.auth.jwt import decode_access_token, is_token_payload_revoked
from app.models.enums import UserRole
from app.models.usuario import Usuario

security = HTTPBearer()


def get_current_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[dict, str]:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    if is_token_payload_revoked(payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
        )
    return payload, token


def get_current_user(
    payload_and_token: tuple[dict, str] = Depends(get_current_payload),
    db: Session = Depends(get_db)
) -> Usuario:
    payload, _ = payload_and_token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    user = db.query(Usuario).filter(Usuario.id == UUID(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return user


def require_roles(*roles: UserRole) -> Callable[[Usuario], Usuario]:
    allowed_roles = set(roles)

    def _role_dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción",
            )
        return current_user

    return _role_dependency


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(UserRole.ADMIN)(current_user)


def require_conductor(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(UserRole.CONDUCTOR)(current_user)


def require_taller(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(UserRole.TALLER)(current_user)


def require_mecanico(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(UserRole.MECANICO)(current_user)
