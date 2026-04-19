from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EstadoComision
from app.models.finanzas import ComisionPlataforma


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
