from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.factura_schema import FacturaRead
from app.services.factura_service import (
    contar_facturas_admin,
    crear_factura_para_pago,
    listar_facturas_admin,
    obtener_factura,
    obtener_factura_por_orden,
    validar_acceso_factura,
)
from app.utils.response import response

router = APIRouter(tags=["Facturas"])


@router.get("/facturas")
def listar_facturas_route(
    orden_id: UUID | None = Query(default=None),
    pago_id: UUID | None = Query(default=None),
    emitida_desde: datetime | None = Query(default=None),
    emitida_hasta: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, gt=0, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    facturas = listar_facturas_admin(
        db,
        orden_id=orden_id,
        pago_id=pago_id,
        emitida_desde=emitida_desde,
        emitida_hasta=emitida_hasta,
        skip=skip,
        limit=limit,
    )
    total = contar_facturas_admin(
        db,
        orden_id=orden_id,
        pago_id=pago_id,
        emitida_desde=emitida_desde,
        emitida_hasta=emitida_hasta,
    )

    data = [FacturaRead.model_validate(item).model_dump() for item in facturas]
    return response(
        status_code=200,
        message="Facturas obtenidas exitosamente",
        data=data,
        count_data=total,
    )


@router.post("/pagos/{pago_id}/factura", status_code=status.HTTP_201_CREATED)
def generar_factura_por_pago_route(
    pago_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        factura = crear_factura_para_pago(db, pago_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = FacturaRead.model_validate(factura).model_dump()
    return response(status_code=201, message="Factura generada exitosamente", data=data)


@router.get("/facturas/{factura_id}")
def obtener_factura_route(
    factura_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    factura = obtener_factura(db, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    if not validar_acceso_factura(db, factura, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta factura")

    data = FacturaRead.model_validate(factura).model_dump()
    return response(status_code=200, message="Factura obtenida exitosamente", data=data)


@router.get("/ordenes/{orden_id}/factura")
def obtener_factura_por_orden_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    factura = obtener_factura_por_orden(db, orden_id)
    if not factura:
        raise HTTPException(status_code=404, detail="La orden no tiene factura")

    if not validar_acceso_factura(db, factura, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta factura")

    data = FacturaRead.model_validate(factura).model_dump()
    return response(status_code=200, message="Factura de orden obtenida exitosamente", data=data)
