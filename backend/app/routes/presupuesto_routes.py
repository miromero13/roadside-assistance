from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_conductor, require_taller
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.presupuesto_schema import (
    PresupuestoCrearRequest,
    PresupuestoRead,
    PresupuestoRechazarRequest,
)
from app.services.presupuesto_service import (
    aprobar_presupuesto,
    crear_presupuesto,
    listar_presupuestos_por_orden,
    rechazar_presupuesto,
)
from app.utils.response import response

router = APIRouter(tags=["Presupuestos"])


@router.post("/ordenes/{orden_id}/presupuestos", status_code=status.HTTP_201_CREATED)
def crear_presupuesto_route(
    orden_id: UUID,
    payload: PresupuestoCrearRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_taller),
):
    try:
        presupuesto = crear_presupuesto(db, orden_id, payload, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = PresupuestoRead.model_validate(presupuesto).model_dump()
    return response(status_code=201, message="Presupuesto creado exitosamente", data=data)


@router.get("/ordenes/{orden_id}/presupuestos")
def listar_presupuestos_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        presupuestos = listar_presupuestos_por_orden(db, orden_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = [PresupuestoRead.model_validate(item).model_dump() for item in presupuestos]
    return response(
        status_code=200,
        message="Presupuestos obtenidos exitosamente",
        data=data,
        count_data=len(data),
    )


@router.put("/presupuestos/{presupuesto_id}/aprobar")
def aprobar_presupuesto_route(
    presupuesto_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    try:
        presupuesto = aprobar_presupuesto(db, presupuesto_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = PresupuestoRead.model_validate(presupuesto).model_dump()
    return response(status_code=200, message="Presupuesto aprobado exitosamente", data=data)


@router.put("/presupuestos/{presupuesto_id}/rechazar")
def rechazar_presupuesto_route(
    presupuesto_id: UUID,
    payload: PresupuestoRechazarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    try:
        presupuesto = rechazar_presupuesto(
            db,
            presupuesto_id,
            current_user,
            payload.motivo_rechazo,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = PresupuestoRead.model_validate(presupuesto).model_dump()
    return response(status_code=200, message="Presupuesto rechazado exitosamente", data=data)
