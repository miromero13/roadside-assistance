from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_conductor
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.usuario import Usuario
from app.schemas.averia_schema import (
    AveriaCrear,
    AveriaDetalleRead,
    AveriaRead,
    MedioAveriaCrear,
    MedioAveriaRead,
)
from app.services.averia_service import (
    agregar_medio_averia,
    crear_averia,
    listar_averias,
    listar_averias_por_usuario,
    obtener_averia,
)
from app.utils.response import response

router = APIRouter(prefix="/averias", tags=["Averías"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_averia_route(
    payload: AveriaCrear,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    try:
        averia = crear_averia(db, payload, current_user.id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = AveriaRead.model_validate(averia).model_dump()
    return response(status_code=201, message="Avería creada exitosamente", data=data)


@router.get("/")
def listar_averias_route(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol == UserRole.ADMIN:
        averias = listar_averias(db)
    elif current_user.rol == UserRole.CONDUCTOR:
        averias = listar_averias_por_usuario(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="No tienes permisos para listar averías")

    data = [AveriaRead.model_validate(item).model_dump() for item in averias]
    return response(
        status_code=200,
        message="Averías obtenidas exitosamente",
        data=data,
        count_data=len(data),
    )


@router.get("/{averia_id}")
def obtener_averia_route(
    averia_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    averia = obtener_averia(db, averia_id)
    if not averia:
        raise HTTPException(status_code=404, detail="Avería no encontrada")

    if current_user.rol != UserRole.ADMIN and averia.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta avería")

    data = AveriaDetalleRead.model_validate(averia).model_dump()
    return response(status_code=200, message="Avería obtenida exitosamente", data=data)


@router.post("/{averia_id}/medios", status_code=status.HTTP_201_CREATED)
def agregar_medio_averia_route(
    averia_id: UUID,
    payload: MedioAveriaCrear,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    averia = obtener_averia(db, averia_id)
    if not averia:
        raise HTTPException(status_code=404, detail="Avería no encontrada")

    if current_user.rol != UserRole.ADMIN and averia.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta avería")

    medio = agregar_medio_averia(db, averia, payload)
    data = MedioAveriaRead.model_validate(medio).model_dump()
    return response(status_code=201, message="Medio agregado exitosamente", data=data)
