from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EstadoComision
from app.models.finanzas import ComisionPlataforma
from app.models.orden import OrdenServicio
from app.models.taller import Taller


def listar_comisiones_admin(
    db: Session,
    estado: EstadoComision | None = None,
    orden_id=None,
    pago_id=None,
    creado_desde=None,
    creado_hasta=None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(ComisionPlataforma)

    if estado is not None:
        query = query.where(ComisionPlataforma.estado == estado)
    if orden_id is not None:
        query = query.where(ComisionPlataforma.orden_id == orden_id)
    if pago_id is not None:
        query = query.where(ComisionPlataforma.pago_id == pago_id)
    if creado_desde is not None:
        query = query.where(ComisionPlataforma.creado_en >= creado_desde)
    if creado_hasta is not None:
        query = query.where(ComisionPlataforma.creado_en <= creado_hasta)

    result = db.execute(
        query.order_by(ComisionPlataforma.creado_en.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


def contar_comisiones_admin(
    db: Session,
    estado: EstadoComision | None = None,
    orden_id=None,
    pago_id=None,
    creado_desde=None,
    creado_hasta=None,
) -> int:
    query = select(ComisionPlataforma)
    if estado is not None:
        query = query.where(ComisionPlataforma.estado == estado)
    if orden_id is not None:
        query = query.where(ComisionPlataforma.orden_id == orden_id)
    if pago_id is not None:
        query = query.where(ComisionPlataforma.pago_id == pago_id)
    if creado_desde is not None:
        query = query.where(ComisionPlataforma.creado_en >= creado_desde)
    if creado_hasta is not None:
        query = query.where(ComisionPlataforma.creado_en <= creado_hasta)
    return len(db.execute(query).scalars().all())


def _obtener_taller_por_usuario(db: Session, usuario_taller_id):
    return db.execute(select(Taller).where(Taller.usuario_id == usuario_taller_id)).scalars().first()


def listar_comisiones_taller(
    db: Session,
    usuario_taller_id,
    estado: EstadoComision | None = None,
    skip: int = 0,
    limit: int = 50,
):
    taller = _obtener_taller_por_usuario(db, usuario_taller_id)
    if not taller:
        return []

    query = (
        select(ComisionPlataforma)
        .join(OrdenServicio, OrdenServicio.id == ComisionPlataforma.orden_id)
        .where(OrdenServicio.taller_id == taller.id)
    )
    if estado is not None:
        query = query.where(ComisionPlataforma.estado == estado)

    result = db.execute(query.order_by(ComisionPlataforma.creado_en.desc()).offset(skip).limit(limit))
    return result.scalars().all()


def contar_comisiones_taller(
    db: Session,
    usuario_taller_id,
    estado: EstadoComision | None = None,
) -> int:
    taller = _obtener_taller_por_usuario(db, usuario_taller_id)
    if not taller:
        return 0

    query = (
        select(ComisionPlataforma)
        .join(OrdenServicio, OrdenServicio.id == ComisionPlataforma.orden_id)
        .where(OrdenServicio.taller_id == taller.id)
    )
    if estado is not None:
        query = query.where(ComisionPlataforma.estado == estado)

    return len(db.execute(query).scalars().all())


def obtener_comision_taller(db: Session, comision_id, usuario_taller_id) -> ComisionPlataforma | None:
    taller = _obtener_taller_por_usuario(db, usuario_taller_id)
    if not taller:
        return None

    return (
        db.execute(
            select(ComisionPlataforma)
            .join(OrdenServicio, OrdenServicio.id == ComisionPlataforma.orden_id)
            .where(ComisionPlataforma.id == comision_id, OrdenServicio.taller_id == taller.id)
        )
        .scalars()
        .first()
    )


def pagar_comision_taller(db: Session, comision: ComisionPlataforma) -> ComisionPlataforma:
    if comision.estado == EstadoComision.PAGADA:
        return comision
    if comision.estado == EstadoComision.ANULADA:
        raise ValueError("No se puede pagar una comisión anulada")

    comision.estado = EstadoComision.PAGADA
    comision.pagado_en = datetime.utcnow()
    db.commit()
    db.refresh(comision)
    return comision
