from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import require_admin
from app.core.database import get_db
from app.models.enums import EstadoComision
from app.models.usuario import Usuario
from app.schemas.comision_schema import ComisionRead
from app.services.comision_service import contar_comisiones_admin, listar_comisiones_admin
from app.utils.response import response

router = APIRouter(prefix="/comisiones", tags=["Comisiones"])


@router.get("/")
def listar_comisiones_route(
    estado: EstadoComision | None = Query(default=None),
    orden_id: UUID | None = Query(default=None),
    pago_id: UUID | None = Query(default=None),
    creado_desde: datetime | None = Query(default=None),
    creado_hasta: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, gt=0, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    comisiones = listar_comisiones_admin(
        db,
        estado=estado,
        orden_id=orden_id,
        pago_id=pago_id,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
        skip=skip,
        limit=limit,
    )
    total = contar_comisiones_admin(
        db,
        estado=estado,
        orden_id=orden_id,
        pago_id=pago_id,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
    )

    data = [ComisionRead.model_validate(item).model_dump() for item in comisiones]
    return response(
        status_code=200,
        message="Comisiones obtenidas exitosamente",
        data=data,
        count_data=total,
    )
