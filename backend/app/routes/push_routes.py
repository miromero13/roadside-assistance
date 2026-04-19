from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.disponibilidad_schema import DispositivoPushRead, DispositivoPushRegistrarRequest
from app.services.push_service import (
    desactivar_dispositivo_push,
    listar_dispositivos_usuario,
    obtener_dispositivo_usuario,
    registrar_dispositivo_push,
)
from app.utils.response import response

router = APIRouter(prefix="/push/dispositivos", tags=["Push"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_dispositivo_route(
    payload: DispositivoPushRegistrarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    dispositivo = registrar_dispositivo_push(
        db,
        current_user,
        payload.plataforma,
        payload.token_push,
    )
    data = DispositivoPushRead.model_validate(dispositivo).model_dump()
    return response(status_code=201, message="Dispositivo push registrado", data=data)


@router.get("/")
def listar_dispositivos_route(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    dispositivos = listar_dispositivos_usuario(db, current_user.id)
    data = [DispositivoPushRead.model_validate(item).model_dump() for item in dispositivos]
    return response(
        status_code=200,
        message="Dispositivos push obtenidos",
        data=data,
        count_data=len(data),
    )


@router.delete("/{dispositivo_id}")
def desactivar_dispositivo_route(
    dispositivo_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    dispositivo = obtener_dispositivo_usuario(db, dispositivo_id, current_user.id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    dispositivo = desactivar_dispositivo_push(db, dispositivo)
    data = DispositivoPushRead.model_validate(dispositivo).model_dump()
    return response(status_code=200, message="Dispositivo push desactivado", data=data)
