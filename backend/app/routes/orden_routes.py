from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_conductor, require_taller
from app.core.database import get_db
from app.models.enums import EstadoOrdenServicio
from app.models.usuario import Usuario
from app.schemas.orden_schema import (
    AsignacionRead,
    AsignarMecanicoRequest,
    HistorialEstadoOrdenRead,
    OrdenAceptarRequest,
    OrdenCancelarRequest,
    OrdenCompletarRequest,
    OrdenCrearPorSeleccionManual,
    OrdenRead,
    OrdenRechazarRequest,
)
from app.services.orden_service import (
    aceptar_orden_por_taller,
    asignar_mecanico_a_orden,
    cancelar_orden,
    completar_orden_manual,
    crear_orden_por_seleccion_manual,
    listar_asignaciones_orden,
    listar_historial_estados_orden,
    listar_ordenes_para_usuario,
    obtener_orden,
    obtener_taller_por_usuario,
    rechazar_orden_por_taller,
    validar_acceso_orden,
)
from app.utils.response import response

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_orden_manual_route(
    payload: OrdenCrearPorSeleccionManual,
    db: Session = Depends(get_db),
    conductor: Usuario = Depends(require_conductor),
):
    try:
        orden = crear_orden_por_seleccion_manual(db, payload, conductor)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = OrdenRead.model_validate(orden).model_dump()
    return response(status_code=201, message="Orden creada exitosamente", data=data)


@router.get("/")
def listar_ordenes_route(
    estado: EstadoOrdenServicio | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    ordenes = listar_ordenes_para_usuario(db, current_user, estado=estado)
    data = [OrdenRead.model_validate(item).model_dump() for item in ordenes]
    return response(
        status_code=200,
        message="Órdenes obtenidas exitosamente",
        data=data,
        count_data=len(data),
    )


@router.get("/{orden_id}")
def obtener_orden_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    if not validar_acceso_orden(db, orden, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta orden")

    data = OrdenRead.model_validate(orden).model_dump()
    return response(status_code=200, message="Orden obtenida exitosamente", data=data)


@router.put("/{orden_id}/aceptar")
def aceptar_orden_route(
    orden_id: UUID,
    payload: OrdenAceptarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_taller),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    taller = obtener_taller_por_usuario(db, current_user.id)
    if not taller:
        raise HTTPException(status_code=400, detail="El usuario no tiene taller asociado")

    try:
        orden = aceptar_orden_por_taller(
            db,
            orden,
            taller,
            current_user,
            payload.tiempo_estimado_respuesta_min,
            payload.tiempo_estimado_llegada_min,
            payload.notas_taller,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = OrdenRead.model_validate(orden).model_dump()
    return response(status_code=200, message="Orden aceptada exitosamente", data=data)


@router.put("/{orden_id}/rechazar")
def rechazar_orden_route(
    orden_id: UUID,
    payload: OrdenRechazarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_taller),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    taller = obtener_taller_por_usuario(db, current_user.id)
    if not taller:
        raise HTTPException(status_code=400, detail="El usuario no tiene taller asociado")

    try:
        orden = rechazar_orden_por_taller(
            db,
            orden,
            taller,
            current_user,
            payload.motivo_rechazo,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = OrdenRead.model_validate(orden).model_dump()
    return response(status_code=200, message="Orden rechazada exitosamente", data=data)


@router.post("/{orden_id}/asignar-mecanico")
def asignar_mecanico_route(
    orden_id: UUID,
    payload: AsignarMecanicoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_taller),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    taller = obtener_taller_por_usuario(db, current_user.id)
    if not taller:
        raise HTTPException(status_code=400, detail="El usuario no tiene taller asociado")

    try:
        asignacion = asignar_mecanico_a_orden(
            db,
            orden,
            taller,
            current_user,
            payload.mecanico_id,
            payload.notas,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = AsignacionRead.model_validate(asignacion).model_dump()
    return response(status_code=200, message="Mecánico asignado exitosamente", data=data)


@router.put("/{orden_id}/cancelar")
def cancelar_orden_route(
    orden_id: UUID,
    payload: OrdenCancelarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    try:
        orden = cancelar_orden(db, orden, current_user, payload.motivo_cancelacion)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = OrdenRead.model_validate(orden).model_dump()
    return response(status_code=200, message="Orden cancelada exitosamente", data=data)


@router.put("/{orden_id}/completar")
def completar_orden_route(
    orden_id: UUID,
    payload: OrdenCompletarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    try:
        orden = completar_orden_manual(db, orden, current_user, payload.observacion)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = OrdenRead.model_validate(orden).model_dump()
    return response(status_code=200, message="Orden completada manualmente", data=data)


@router.get("/{orden_id}/historial-estados")
def historial_estados_orden_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if not validar_acceso_orden(db, orden, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver el historial")

    historial = listar_historial_estados_orden(db, orden_id)
    data = [HistorialEstadoOrdenRead.model_validate(item).model_dump() for item in historial]
    return response(
        status_code=200,
        message="Historial de estados obtenido exitosamente",
        data=data,
        count_data=len(data),
    )


@router.get("/{orden_id}/asignaciones")
def listar_asignaciones_orden_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if not validar_acceso_orden(db, orden, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver asignaciones")

    asignaciones = listar_asignaciones_orden(db, orden_id)
    data = [AsignacionRead.model_validate(item).model_dump() for item in asignaciones]
    return response(
        status_code=200,
        message="Asignaciones de orden obtenidas exitosamente",
        data=data,
        count_data=len(data),
    )
