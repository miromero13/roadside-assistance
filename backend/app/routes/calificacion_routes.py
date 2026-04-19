from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_conductor
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.calificacion_schema import CalificacionCrearRequest, CalificacionRead
from app.services.calificacion_service import crear_calificacion_orden, listar_calificaciones_orden
from app.services.orden_service import obtener_orden, validar_acceso_orden
from app.utils.response import response

router = APIRouter(prefix="/ordenes", tags=["Calificaciones"])


@router.post("/{orden_id}/calificaciones", status_code=status.HTTP_201_CREATED)
def crear_calificacion_route(
    orden_id: UUID,
    payload: CalificacionCrearRequest,
    db: Session = Depends(get_db),
    conductor: Usuario = Depends(require_conductor),
):
    try:
        calificacion = crear_calificacion_orden(
            db,
            orden_id,
            conductor,
            payload.puntuacion,
            payload.comentario,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = CalificacionRead.model_validate(calificacion).model_dump()
    return response(status_code=201, message="Calificación registrada exitosamente", data=data)


@router.get("/{orden_id}/calificaciones")
def listar_calificaciones_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    if not validar_acceso_orden(db, orden, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver calificaciones")

    calificaciones = listar_calificaciones_orden(db, orden_id)
    data = [CalificacionRead.model_validate(item).model_dump() for item in calificaciones]
    return response(
        status_code=200,
        message="Calificaciones obtenidas exitosamente",
        data=data,
        count_data=len(data),
    )
