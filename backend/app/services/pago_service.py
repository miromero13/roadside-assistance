from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.enums import (
    EstadoComision,
    EstadoOrdenServicio,
    EstadoPago,
    EstadoPresupuesto,
    TipoNotificacion,
    UserRole,
)
from app.models.finanzas import ComisionPlataforma, Pago, Presupuesto
from app.models.orden import OrdenServicio
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.schemas.pago_schema import PagoCrearRequest
from app.services.notificacion_service import notificar_a_conductor_y_taller_por_orden
from app.services.notificacion_service import notificar_a_mecanicos_activos_por_orden
from app.services.metrica_service import recalcular_metrica_orden
from app.services.orden_service import _registrar_historial_orden
from app.services.payment_gateway import DummyPaymentGateway


def obtener_pago(db: Session, pago_id) -> Pago | None:
    return db.execute(select(Pago).where(Pago.id == pago_id)).scalars().first()


def listar_pagos_admin(
    db: Session,
    estado: EstadoPago | None = None,
    metodo=None,
    orden_id=None,
    creado_desde=None,
    creado_hasta=None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(Pago)
    if estado is not None:
        query = query.where(Pago.estado == estado)
    if metodo is not None:
        query = query.where(Pago.metodo == metodo)
    if orden_id is not None:
        query = query.where(Pago.orden_id == orden_id)
    if creado_desde is not None:
        query = query.where(Pago.creado_en >= creado_desde)
    if creado_hasta is not None:
        query = query.where(Pago.creado_en <= creado_hasta)

    result = db.execute(query.order_by(Pago.creado_en.desc()).offset(skip).limit(limit))
    return result.scalars().all()


def contar_pagos_admin(
    db: Session,
    estado: EstadoPago | None = None,
    metodo=None,
    orden_id=None,
    creado_desde=None,
    creado_hasta=None,
) -> int:
    query = select(Pago)
    if estado is not None:
        query = query.where(Pago.estado == estado)
    if metodo is not None:
        query = query.where(Pago.metodo == metodo)
    if orden_id is not None:
        query = query.where(Pago.orden_id == orden_id)
    if creado_desde is not None:
        query = query.where(Pago.creado_en >= creado_desde)
    if creado_hasta is not None:
        query = query.where(Pago.creado_en <= creado_hasta)
    return len(db.execute(query).scalars().all())


def _es_conductor_dueno_orden(db: Session, orden: OrdenServicio, usuario_id) -> bool:
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    return bool(averia and averia.usuario_id == usuario_id)


def _es_taller_dueno_orden(db: Session, orden: OrdenServicio, usuario_id) -> bool:
    taller = db.execute(select(Taller).where(Taller.usuario_id == usuario_id)).scalars().first()
    return bool(taller and taller.id == orden.taller_id)


def validar_acceso_pago(db: Session, pago: Pago, usuario: Usuario) -> bool:
    if usuario.rol == UserRole.ADMIN:
        return True

    orden = db.execute(select(OrdenServicio).where(OrdenServicio.id == pago.orden_id)).scalars().first()
    if not orden:
        return False

    if usuario.rol == UserRole.CONDUCTOR:
        return _es_conductor_dueno_orden(db, orden, usuario.id)
    if usuario.rol == UserRole.TALLER:
        return _es_taller_dueno_orden(db, orden, usuario.id)
    return False


def crear_pago(db: Session, payload: PagoCrearRequest, conductor: Usuario) -> Pago:
    if conductor.rol != UserRole.CONDUCTOR:
        raise PermissionError("Solo un conductor puede crear pagos")

    orden = db.execute(select(OrdenServicio).where(OrdenServicio.id == payload.orden_id)).scalars().first()
    if not orden:
        raise ValueError("La orden no existe")
    if not _es_conductor_dueno_orden(db, orden, conductor.id):
        raise PermissionError("No puedes pagar una orden que no te pertenece")
    if orden.estado in {
        EstadoOrdenServicio.RECHAZADA,
        EstadoOrdenServicio.CANCELADA,
        EstadoOrdenServicio.COMPLETADA,
    }:
        raise ValueError("La orden no está disponible para pago")

    pago_existente = db.execute(select(Pago.id).where(Pago.orden_id == orden.id).limit(1)).scalar_one_or_none()
    if pago_existente:
        raise ValueError("La orden ya tiene un pago registrado")

    presupuesto = db.execute(
        select(Presupuesto).where(
            Presupuesto.id == payload.presupuesto_id,
            Presupuesto.orden_id == orden.id,
        )
    ).scalars().first()
    if not presupuesto:
        raise ValueError("El presupuesto no existe para la orden")
    if presupuesto.estado != EstadoPresupuesto.APROBADO:
        raise ValueError("Solo se puede pagar un presupuesto aprobado")

    monto_payload = Decimal(str(payload.monto))
    monto_presupuesto = Decimal(str(presupuesto.monto_total))
    if monto_payload != monto_presupuesto:
        raise ValueError("El monto del pago debe ser exactamente igual al presupuesto aprobado")

    gateway = DummyPaymentGateway()
    intencion = gateway.crear_intencion_pago(monto_payload, payload.metodo)

    pago = Pago(
        orden_id=orden.id,
        presupuesto_id=presupuesto.id,
        monto=monto_payload,
        metodo=payload.metodo,
        estado=EstadoPago.PENDIENTE,
        referencia_externa=intencion.referencia_externa,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def confirmar_pago(db: Session, pago: Pago, referencia_externa: str | None = None) -> Pago:
    if pago.estado == EstadoPago.COMPLETADO:
        return pago

    referencia = referencia_externa or pago.referencia_externa
    if not referencia:
        raise ValueError("No existe referencia externa para confirmar el pago")

    pago_duplicado = db.execute(
        select(Pago).where(
            Pago.referencia_externa == referencia,
            Pago.id != pago.id,
            Pago.estado == EstadoPago.COMPLETADO,
        )
    ).scalars().first()
    if pago_duplicado:
        raise ValueError("La referencia externa ya fue usada por otro pago completado")

    gateway = DummyPaymentGateway()
    confirmado = gateway.confirmar_pago(referencia)
    if not confirmado:
        pago.estado = EstadoPago.FALLIDO
        db.commit()
        db.refresh(pago)
        return pago

    pago.estado = EstadoPago.COMPLETADO
    pago.referencia_externa = referencia
    pago.pagado_en = datetime.utcnow()

    comision_existente = db.execute(
        select(ComisionPlataforma).where(ComisionPlataforma.pago_id == pago.id)
    ).scalars().first()
    if not comision_existente:
        porcentaje = Decimal("10.00")
        monto_base = Decimal(str(pago.monto))
        monto_comision = (monto_base * porcentaje) / Decimal("100")
        comision = ComisionPlataforma(
            orden_id=pago.orden_id,
            pago_id=pago.id,
            monto_base=monto_base,
            porcentaje=porcentaje,
            monto_comision=monto_comision,
            estado=EstadoComision.PENDIENTE,
        )
        db.add(comision)

    orden = db.execute(select(OrdenServicio).where(OrdenServicio.id == pago.orden_id)).scalars().first()
    if not orden:
        raise ValueError("La orden asociada no existe")
    if orden.estado != EstadoOrdenServicio.COMPLETADA:
        estado_anterior = orden.estado
        orden.estado = EstadoOrdenServicio.COMPLETADA
        orden.completado_en = datetime.utcnow()
        _registrar_historial_orden(
            db,
            orden,
            estado_anterior,
            EstadoOrdenServicio.COMPLETADA,
            None,
            observacion="Orden completada automáticamente por pago exitoso",
        )
        notificar_a_conductor_y_taller_por_orden(
            db,
            orden,
            TipoNotificacion.PAGO_COMPLETADO,
            "Pago completado",
            "El pago fue confirmado y la orden se marco como completada.",
        )
        notificar_a_mecanicos_activos_por_orden(
            db,
            orden,
            TipoNotificacion.ORDEN_ACTUALIZADA,
            "Orden completada",
            "La orden fue completada tras confirmar el pago.",
        )

    recalcular_metrica_orden(db, orden)

    db.commit()
    db.refresh(pago)
    return pago
