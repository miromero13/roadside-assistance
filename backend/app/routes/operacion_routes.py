from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.operacion_schema import (
    MecanicoDisponibilidadRequest,
    TallerActualizarRequest,
    TallerRead,
)
from app.services.operacion_service import (
    actualizar_disponibilidad_mecanico,
    actualizar_taller,
    obtener_mecanico,
    obtener_taller,
)
from app.utils.response import response

router = APIRouter(tags=["Operación"])


@router.patch("/mecanicos/{mecanico_id}/disponibilidad")
def actualizar_disponibilidad_mecanico_route(
    mecanico_id: UUID,
    payload: MecanicoDisponibilidadRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    mecanico = obtener_mecanico(db, mecanico_id)
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecánico no encontrado")

    try:
        mecanico = actualizar_disponibilidad_mecanico(db, mecanico, payload.disponible, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return response(
        status_code=200,
        message="Disponibilidad de mecánico actualizada",
        data={
            "id": str(mecanico.id),
            "disponible": mecanico.disponible,
        },
    )


@router.get("/talleres/{taller_id}")
def obtener_taller_route(
    taller_id: UUID,
    db: Session = Depends(get_db),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    data = TallerRead.model_validate(taller).model_dump()
    return response(status_code=200, message="Taller obtenido exitosamente", data=data)


@router.patch("/talleres/{taller_id}")
def actualizar_taller_route(
    taller_id: UUID,
    payload: TallerActualizarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    try:
        taller = actualizar_taller(db, taller, current_user, data)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    result = TallerRead.model_validate(taller).model_dump()
    return response(status_code=200, message="Taller actualizado exitosamente", data=result)
