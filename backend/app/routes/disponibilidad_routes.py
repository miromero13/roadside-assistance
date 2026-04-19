from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.disponibilidad_schema import (
    BloqueoTallerCrearRequest,
    BloqueoTallerRead,
    HorarioTallerActualizarRequest,
    HorarioTallerCrearRequest,
    HorarioTallerRead,
)
from app.services.disponibilidad_service import (
    crear_bloqueo_taller,
    crear_horario_taller,
    eliminar_bloqueo_taller,
    eliminar_horario_taller,
    listar_bloqueos_taller,
    listar_horarios_taller,
    obtener_bloqueo,
    obtener_horario,
    obtener_taller,
    actualizar_horario_taller,
)
from app.utils.response import response

router = APIRouter(tags=["Disponibilidad"])


@router.get("/talleres/{taller_id}/horarios")
def listar_horarios_route(
    taller_id: UUID,
    db: Session = Depends(get_db),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    horarios = listar_horarios_taller(db, taller_id)
    data = [HorarioTallerRead.model_validate(item).model_dump() for item in horarios]
    return response(status_code=200, message="Horarios obtenidos exitosamente", data=data, count_data=len(data))


@router.post("/talleres/{taller_id}/horarios", status_code=status.HTTP_201_CREATED)
def crear_horario_route(
    taller_id: UUID,
    payload: HorarioTallerCrearRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    try:
        horario = crear_horario_taller(db, taller, current_user, payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    data = HorarioTallerRead.model_validate(horario).model_dump()
    return response(status_code=201, message="Horario creado exitosamente", data=data)


@router.patch("/talleres/{taller_id}/horarios/{horario_id}")
def actualizar_horario_route(
    taller_id: UUID,
    horario_id: UUID,
    payload: HorarioTallerActualizarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    horario = obtener_horario(db, horario_id, taller_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    data_update = payload.model_dump(exclude_unset=True)
    if not data_update:
        raise HTTPException(status_code=400, detail="No se enviaron cambios para actualizar")

    try:
        horario = actualizar_horario_taller(db, horario, taller, current_user, data_update)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    data = HorarioTallerRead.model_validate(horario).model_dump()
    return response(status_code=200, message="Horario actualizado exitosamente", data=data)


@router.delete("/talleres/{taller_id}/horarios/{horario_id}")
def eliminar_horario_route(
    taller_id: UUID,
    horario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    horario = obtener_horario(db, horario_id, taller_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    try:
        eliminar_horario_taller(db, horario, taller, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return response(status_code=200, message="Horario eliminado exitosamente")


@router.get("/talleres/{taller_id}/bloqueos")
def listar_bloqueos_route(
    taller_id: UUID,
    db: Session = Depends(get_db),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    bloqueos = listar_bloqueos_taller(db, taller_id)
    data = [BloqueoTallerRead.model_validate(item).model_dump() for item in bloqueos]
    return response(status_code=200, message="Bloqueos obtenidos exitosamente", data=data, count_data=len(data))


@router.post("/talleres/{taller_id}/bloqueos", status_code=status.HTTP_201_CREATED)
def crear_bloqueo_route(
    taller_id: UUID,
    payload: BloqueoTallerCrearRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    try:
        bloqueo = crear_bloqueo_taller(db, taller, current_user, payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = BloqueoTallerRead.model_validate(bloqueo).model_dump()
    return response(status_code=201, message="Bloqueo creado exitosamente", data=data)


@router.delete("/talleres/{taller_id}/bloqueos/{bloqueo_id}")
def eliminar_bloqueo_route(
    taller_id: UUID,
    bloqueo_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    bloqueo = obtener_bloqueo(db, bloqueo_id, taller_id)
    if not bloqueo:
        raise HTTPException(status_code=404, detail="Bloqueo no encontrado")

    try:
        eliminar_bloqueo_taller(db, bloqueo, taller, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return response(status_code=200, message="Bloqueo eliminado exitosamente")
