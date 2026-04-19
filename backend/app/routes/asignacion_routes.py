from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import require_mecanico
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.orden_schema import AsignacionEstadoRequest, AsignacionRead
from app.services.asignacion_service import (
    actualizar_estado_asignacion,
    obtener_asignacion,
    obtener_mecanico_por_usuario,
)
from app.utils.response import response

router = APIRouter(prefix="/asignaciones", tags=["Asignaciones"])


@router.put("/{asignacion_id}/estado")
def actualizar_estado_asignacion_route(
    asignacion_id: UUID,
    payload: AsignacionEstadoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_mecanico),
):
    asignacion = obtener_asignacion(db, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    mecanico = obtener_mecanico_por_usuario(db, current_user.id)
    if not mecanico:
        raise HTTPException(status_code=400, detail="El usuario no tiene perfil de mecánico")

    try:
        asignacion_actualizada = actualizar_estado_asignacion(
            db,
            asignacion,
            mecanico,
            current_user,
            payload.estado,
            payload.notas,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = AsignacionRead.model_validate(asignacion_actualizada).model_dump()
    return response(status_code=200, message="Estado de asignación actualizado", data=data)
