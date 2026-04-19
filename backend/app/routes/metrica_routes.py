from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import require_admin
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.metrica_schema import MetricaServicioRead
from app.services.metrica_service import contar_metricas, listar_metricas, recalcular_metrica_orden
from app.services.orden_service import obtener_orden
from app.utils.response import response

router = APIRouter(prefix="/metricas", tags=["Métricas"])


@router.post("/ordenes/{orden_id}/recalcular")
def recalcular_metrica_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    try:
        metrica = recalcular_metrica_orden(db, orden)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = MetricaServicioRead.model_validate(metrica).model_dump()
    return response(status_code=200, message="Métrica recalculada exitosamente", data=data)


@router.get("/ordenes")
def listar_metricas_route(
    orden_id: UUID | None = Query(default=None),
    creado_desde: datetime | None = Query(default=None),
    creado_hasta: datetime | None = Query(default=None),
    calificacion_min: float | None = Query(default=None, ge=0, le=5),
    calificacion_max: float | None = Query(default=None, ge=0, le=5),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, gt=0, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    metricas = listar_metricas(
        db,
        orden_id=orden_id,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
        calificacion_min=calificacion_min,
        calificacion_max=calificacion_max,
        skip=skip,
        limit=limit,
    )
    total = contar_metricas(
        db,
        orden_id=orden_id,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
        calificacion_min=calificacion_min,
        calificacion_max=calificacion_max,
    )
    data = [MetricaServicioRead.model_validate(item).model_dump() for item in metricas]
    return response(
        status_code=200,
        message="Métricas obtenidas exitosamente",
        data=data,
        count_data=total,
    )
