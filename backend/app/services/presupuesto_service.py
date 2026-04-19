from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.enums import EstadoOrdenServicio, EstadoPresupuesto, TipoNotificacion, UserRole
from app.models.finanzas import Presupuesto
from app.models.orden import OrdenServicio
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.schemas.presupuesto_schema import PresupuestoCrearRequest
from app.services.notificacion_service import (
    notificar_a_conductor_por_orden,
    notificar_a_taller_por_orden,
)


ESTADOS_ORDEN_PERMITIDOS_PRESUPUESTO = {
    EstadoOrdenServicio.ACEPTADA,
    EstadoOrdenServicio.TECNICO_ASIGNADO,
    EstadoOrdenServicio.EN_CAMINO,
    EstadoOrdenServicio.EN_PROCESO,
}


def obtener_orden(db: Session, orden_id) -> OrdenServicio | None:
    return db.execute(select(OrdenServicio).where(OrdenServicio.id == orden_id)).scalars().first()


def obtener_presupuesto(db: Session, presupuesto_id) -> Presupuesto | None:
    return db.execute(select(Presupuesto).where(Presupuesto.id == presupuesto_id)).scalars().first()


def _es_taller_dueno_orden(db: Session, usuario_taller_id, orden: OrdenServicio) -> bool:
    taller = db.execute(select(Taller).where(Taller.usuario_id == usuario_taller_id)).scalars().first()
    return bool(taller and taller.id == orden.taller_id)


def _es_conductor_dueno_orden(db: Session, usuario_conductor_id, orden: OrdenServicio) -> bool:
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    return bool(averia and averia.usuario_id == usuario_conductor_id)


def _existe_presupuesto_aprobado(db: Session, orden_id, excluir_presupuesto_id=None) -> bool:
    query = select(Presupuesto.id).where(
        Presupuesto.orden_id == orden_id,
        Presupuesto.estado == EstadoPresupuesto.APROBADO,
    )
    if excluir_presupuesto_id is not None:
        query = query.where(Presupuesto.id != excluir_presupuesto_id)

    return db.execute(query.limit(1)).scalar_one_or_none() is not None


def crear_presupuesto(
    db: Session,
    orden_id,
    payload: PresupuestoCrearRequest,
    usuario_taller: Usuario,
) -> Presupuesto:
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise ValueError("La orden no existe")

    if usuario_taller.rol != UserRole.TALLER:
        raise PermissionError("Solo un taller puede crear presupuestos")

    if not _es_taller_dueno_orden(db, usuario_taller.id, orden):
        raise PermissionError("No puedes crear presupuestos para órdenes de otro taller")

    if orden.estado not in ESTADOS_ORDEN_PERMITIDOS_PRESUPUESTO:
        raise ValueError("La orden no está en un estado válido para generar presupuesto")

    if _existe_presupuesto_aprobado(db, orden.id):
        raise ValueError("La orden ya tiene un presupuesto aprobado")

    version_actual = db.execute(
        select(func.max(Presupuesto.version)).where(Presupuesto.orden_id == orden.id)
    ).scalar_one_or_none()
    siguiente_version = (version_actual or 0) + 1

    monto_repuestos = Decimal(str(payload.monto_repuestos))
    monto_mano_obra = Decimal(str(payload.monto_mano_obra))
    monto_total = monto_repuestos + monto_mano_obra

    presupuesto = Presupuesto(
        orden_id=orden.id,
        version=siguiente_version,
        descripcion_trabajos=payload.descripcion_trabajos,
        items_detalle=payload.items_detalle,
        monto_repuestos=monto_repuestos,
        monto_mano_obra=monto_mano_obra,
        monto_total=monto_total,
        estado=EstadoPresupuesto.ENVIADO,
    )
    db.add(presupuesto)
    notificar_a_conductor_por_orden(
        db,
        orden,
        TipoNotificacion.PRESUPUESTO_ENVIADO,
        "Presupuesto enviado",
        "El taller envio un presupuesto para tu orden.",
    )
    db.commit()
    db.refresh(presupuesto)
    return presupuesto


def listar_presupuestos_por_orden(
    db: Session,
    orden_id,
    usuario_actual: Usuario,
) -> list[Presupuesto]:
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise ValueError("La orden no existe")

    acceso = False
    if usuario_actual.rol == UserRole.ADMIN:
        acceso = True
    elif usuario_actual.rol == UserRole.TALLER:
        acceso = _es_taller_dueno_orden(db, usuario_actual.id, orden)
    elif usuario_actual.rol == UserRole.CONDUCTOR:
        acceso = _es_conductor_dueno_orden(db, usuario_actual.id, orden)

    if not acceso:
        raise PermissionError("No tienes permisos para ver los presupuestos de esta orden")

    result = db.execute(
        select(Presupuesto)
        .where(Presupuesto.orden_id == orden_id)
        .order_by(Presupuesto.version.desc())
    )
    return result.scalars().all()


def aprobar_presupuesto(
    db: Session,
    presupuesto_id,
    usuario_conductor: Usuario,
) -> Presupuesto:
    presupuesto = obtener_presupuesto(db, presupuesto_id)
    if not presupuesto:
        raise ValueError("El presupuesto no existe")

    orden = obtener_orden(db, presupuesto.orden_id)
    if not orden:
        raise ValueError("La orden asociada no existe")

    if usuario_conductor.rol != UserRole.CONDUCTOR:
        raise PermissionError("Solo un conductor puede aprobar presupuestos")

    if not _es_conductor_dueno_orden(db, usuario_conductor.id, orden):
        raise PermissionError("No puedes aprobar presupuestos de otra orden")

    if presupuesto.estado == EstadoPresupuesto.APROBADO:
        raise ValueError("El presupuesto ya fue aprobado")
    if presupuesto.estado in {EstadoPresupuesto.RECHAZADO, EstadoPresupuesto.VENCIDO}:
        raise ValueError("No se puede aprobar un presupuesto rechazado o vencido")
    if _existe_presupuesto_aprobado(db, orden.id, excluir_presupuesto_id=presupuesto.id):
        raise ValueError("La orden ya tiene otro presupuesto aprobado")

    presupuesto.estado = EstadoPresupuesto.APROBADO
    presupuesto.motivo_rechazo = None
    presupuesto.respondido_en = datetime.utcnow()

    otros_enviados = db.execute(
        select(Presupuesto).where(
            Presupuesto.orden_id == orden.id,
            Presupuesto.id != presupuesto.id,
            Presupuesto.estado == EstadoPresupuesto.ENVIADO,
        )
    ).scalars().all()

    for otro in otros_enviados:
        otro.estado = EstadoPresupuesto.VENCIDO
        otro.respondido_en = datetime.utcnow()

    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.PRESUPUESTO_APROBADO,
        "Presupuesto aprobado",
        "El conductor aprobo el presupuesto de la orden.",
    )

    db.commit()
    db.refresh(presupuesto)
    return presupuesto


def rechazar_presupuesto(
    db: Session,
    presupuesto_id,
    usuario_conductor: Usuario,
    motivo_rechazo: str,
) -> Presupuesto:
    presupuesto = obtener_presupuesto(db, presupuesto_id)
    if not presupuesto:
        raise ValueError("El presupuesto no existe")

    orden = obtener_orden(db, presupuesto.orden_id)
    if not orden:
        raise ValueError("La orden asociada no existe")

    if usuario_conductor.rol != UserRole.CONDUCTOR:
        raise PermissionError("Solo un conductor puede rechazar presupuestos")

    if not _es_conductor_dueno_orden(db, usuario_conductor.id, orden):
        raise PermissionError("No puedes rechazar presupuestos de otra orden")

    if presupuesto.estado == EstadoPresupuesto.APROBADO:
        raise ValueError("No se puede rechazar un presupuesto aprobado")
    if presupuesto.estado == EstadoPresupuesto.RECHAZADO:
        raise ValueError("El presupuesto ya fue rechazado")
    if presupuesto.estado == EstadoPresupuesto.VENCIDO:
        raise ValueError("No se puede rechazar un presupuesto vencido")

    presupuesto.estado = EstadoPresupuesto.RECHAZADO
    presupuesto.motivo_rechazo = motivo_rechazo
    presupuesto.respondido_en = datetime.utcnow()

    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.MENSAJE_NUEVO,
        "Presupuesto rechazado",
        "El conductor rechazo el presupuesto enviado.",
    )

    db.commit()
    db.refresh(presupuesto)
    return presupuesto
