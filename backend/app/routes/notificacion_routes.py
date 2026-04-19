from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.notificacion_schema import NotificacionRead
from app.services.notificacion_service import (
    contar_notificaciones_usuario,
    listar_notificaciones_usuario,
    marcar_notificacion_leida,
    marcar_todas_leidas_usuario,
    obtener_notificacion_de_usuario,
)
from app.utils.response import response

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("/")
def listar_notificaciones_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
    solo_no_leidas: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    notificaciones = listar_notificaciones_usuario(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        solo_no_leidas=solo_no_leidas,
    )
    total = contar_notificaciones_usuario(db, current_user.id, solo_no_leidas=solo_no_leidas)
    data = [NotificacionRead.model_validate(item).model_dump() for item in notificaciones]
    return response(
        status_code=200,
        message="Notificaciones obtenidas exitosamente",
        data=data,
        count_data=total,
    )


@router.put("/leer-todas")
def leer_todas_notificaciones_route(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    total_marcadas = marcar_todas_leidas_usuario(db, current_user.id)
    return response(
        status_code=200,
        message="Notificaciones marcadas como leidas",
        data={"total_marcadas": total_marcadas},
    )


@router.put("/{notificacion_id}/leer")
def leer_notificacion_route(
    notificacion_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    notificacion = obtener_notificacion_de_usuario(db, notificacion_id, current_user.id)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notificacion = marcar_notificacion_leida(db, notificacion)
    data = NotificacionRead.model_validate(notificacion).model_dump()
    return response(status_code=200, message="Notificación marcada como leída", data=data)
