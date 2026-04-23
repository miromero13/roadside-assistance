from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.user_schema import (
    UsuarioActualizarPerfil,
    UsuarioActualizarRol,
    UsuarioCrear,
    UsuarioRead,
    UsuariosPaginadosResponse,
)
from app.services.user_service import (
    create_user,
    get_user,
    get_users,
    get_users_count,
    update_user_profile,
    update_user_rol,
)
from app.core.database import get_db
from app.utils.response import response
from app.auth.dependencies import get_current_user, require_admin
from app.models.enums import UserRole
from app.models.usuario import Usuario

router = APIRouter(prefix="/users", tags=["Usuarios"])

# 🚀 Crea usuario (público)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_route(
    user: UsuarioCrear,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    try:
        db_user = create_user(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    user_data = UsuarioRead.model_validate(db_user).model_dump()
    return response(
        status_code=201,
        message="Usuario creado exitosamente",
        data=user_data
    )

# ✅ GET /users/me → DEBE IR ANTES que /{user_id}
@router.get("/me")
async def get_me_route(current_user: Usuario = Depends(get_current_user)):
    # Valida con Pydantic y serializa:
    user_data = UsuarioRead.model_validate(current_user).model_dump()
    return response(
        status_code=200,
        message="Perfil obtenido correctamente",
        data=user_data
    )

# ✅ GET /users/{user_id}
@router.get("/{user_id}")
async def get_user_route(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este usuario")

    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {user_id} no encontrado")
    user_data = UsuarioRead.model_validate(db_user).model_dump()
    return response(
        status_code=200,
        message="Usuario obtenido exitosamente",
        data=user_data
    )


@router.put("/me")
async def update_me_route(
    payload: UsuarioActualizarPerfil,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        updated_user = update_user_profile(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user_data = UsuarioRead.model_validate(updated_user).model_dump()
    return response(
        status_code=200,
        message="Perfil actualizado correctamente",
        data=user_data,
    )

# ✅ GET /users/ → listado, protegido si quieres
@router.get("/", response_model=UsuariosPaginadosResponse)
async def get_users_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin)
):
    users = get_users(db, skip, limit)
    total = get_users_count(db)

    users_data = [UsuarioRead.model_validate(user).model_dump() for user in users]

    return response(
        status_code=200,
        message="Usuarios obtenidos exitosamente",
        data=users_data,
        count_data=total,
    )


@router.patch("/{user_id}/rol")
async def update_user_rol_route(
    user_id: UUID,
    update_data: UsuarioActualizarRol,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol")

    db_user = update_user_rol(db, user_id, update_data)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {user_id} no encontrado")

    user_data = UsuarioRead.model_validate(db_user).model_dump()
    return response(
        status_code=200,
        message="Rol de usuario actualizado exitosamente",
        data=user_data
    )
