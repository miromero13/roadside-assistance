from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_admin, require_conductor
from app.core.database import get_db
from app.models.enums import EstadoPago, MetodoPago
from app.models.usuario import Usuario
from app.schemas.pago_schema import PagoConfirmarRequest, PagoCrearRequest, PagoRead
from app.services.pago_service import (
    confirmar_pago,
    contar_pagos_admin,
    crear_pago,
    listar_pagos_admin,
    obtener_pago,
    validar_acceso_pago,
)
from app.utils.response import response

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.get("/")
def listar_pagos_route(
    estado: EstadoPago | None = Query(default=None),
    metodo: MetodoPago | None = Query(default=None),
    orden_id: UUID | None = Query(default=None),
    creado_desde: datetime | None = Query(default=None),
    creado_hasta: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, gt=0, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    pagos = listar_pagos_admin(
        db,
        estado=estado,
        metodo=metodo,
        orden_id=orden_id,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
        skip=skip,
        limit=limit,
    )
    total = contar_pagos_admin(
        db,
        estado=estado,
        metodo=metodo,
        orden_id=orden_id,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
    )
    data = [PagoRead.model_validate(item).model_dump() for item in pagos]
    return response(
        status_code=200,
        message="Pagos obtenidos exitosamente",
        data=data,
        count_data=total,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_pago_route(
    payload: PagoCrearRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    try:
        pago = crear_pago(db, payload, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = PagoRead.model_validate(pago).model_dump()
    return response(status_code=201, message="Pago creado exitosamente", data=data)


@router.get("/{pago_id}")
def obtener_pago_route(
    pago_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    pago = obtener_pago(db, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    if not validar_acceso_pago(db, pago, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este pago")

    data = PagoRead.model_validate(pago).model_dump()
    return response(status_code=200, message="Pago obtenido exitosamente", data=data)


@router.post("/{pago_id}/confirmar")
def confirmar_pago_route(
    pago_id: UUID,
    payload: PagoConfirmarRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    pago = obtener_pago(db, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    try:
        pago = confirmar_pago(db, pago, payload.referencia_externa)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = PagoRead.model_validate(pago).model_dump()
    return response(status_code=200, message="Pago confirmado exitosamente", data=data)
