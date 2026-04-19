from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.comunicacion import Calificacion
from app.models.enums import EstadoOrdenServicio
from app.models.orden import AsignacionOrden, MetricaServicio, OrdenServicio


def _diff_minutes(inicio, fin) -> int | None:
    if inicio is None or fin is None:
        return None
    delta = fin - inicio
    return max(int(delta.total_seconds() // 60), 0)


def obtener_metrica_por_orden(db: Session, orden_id) -> MetricaServicio | None:
    return db.execute(select(MetricaServicio).where(MetricaServicio.orden_id == orden_id)).scalars().first()


def recalcular_metrica_orden(db: Session, orden: OrdenServicio) -> MetricaServicio:
    if orden.estado != EstadoOrdenServicio.COMPLETADA:
        raise ValueError("Solo se pueden calcular métricas para órdenes completadas")

    metrica = obtener_metrica_por_orden(db, orden.id)
    if not metrica:
        metrica = MetricaServicio(orden_id=orden.id)
        db.add(metrica)

    primera_asignacion = (
        db.execute(
            select(AsignacionOrden)
            .where(AsignacionOrden.orden_id == orden.id)
            .order_by(AsignacionOrden.asignado_en.asc())
            .limit(1)
        )
        .scalars()
        .first()
    )

    metrica.tiempo_respuesta_min = _diff_minutes(orden.creado_en, orden.aceptado_en)
    metrica.tiempo_llegada_min = _diff_minutes(
        primera_asignacion.asignado_en if primera_asignacion else None,
        primera_asignacion.llegada_en if primera_asignacion else None,
    )
    metrica.tiempo_resolucion_min = _diff_minutes(orden.iniciado_en, orden.completado_en)

    promedio_calificacion = db.execute(
        select(func.avg(Calificacion.puntuacion)).where(Calificacion.orden_id == orden.id)
    ).scalar_one_or_none()
    metrica.calificacion_final = (
        Decimal(str(round(float(promedio_calificacion), 2))) if promedio_calificacion is not None else None
    )

    db.commit()
    db.refresh(metrica)
    return metrica


def listar_metricas(
    db: Session,
    orden_id=None,
    creado_desde=None,
    creado_hasta=None,
    calificacion_min=None,
    calificacion_max=None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(MetricaServicio)
    if orden_id is not None:
        query = query.where(MetricaServicio.orden_id == orden_id)
    if creado_desde is not None:
        query = query.where(MetricaServicio.creado_en >= creado_desde)
    if creado_hasta is not None:
        query = query.where(MetricaServicio.creado_en <= creado_hasta)
    if calificacion_min is not None:
        query = query.where(MetricaServicio.calificacion_final >= calificacion_min)
    if calificacion_max is not None:
        query = query.where(MetricaServicio.calificacion_final <= calificacion_max)

    result = db.execute(query.order_by(MetricaServicio.creado_en.desc()).offset(skip).limit(limit))
    return result.scalars().all()


def contar_metricas(
    db: Session,
    orden_id=None,
    creado_desde=None,
    creado_hasta=None,
    calificacion_min=None,
    calificacion_max=None,
) -> int:
    query = select(MetricaServicio)
    if orden_id is not None:
        query = query.where(MetricaServicio.orden_id == orden_id)
    if creado_desde is not None:
        query = query.where(MetricaServicio.creado_en >= creado_desde)
    if creado_hasta is not None:
        query = query.where(MetricaServicio.creado_en <= creado_hasta)
    if calificacion_min is not None:
        query = query.where(MetricaServicio.calificacion_final >= calificacion_min)
    if calificacion_max is not None:
        query = query.where(MetricaServicio.calificacion_final <= calificacion_max)
    return len(db.execute(query).scalars().all())
