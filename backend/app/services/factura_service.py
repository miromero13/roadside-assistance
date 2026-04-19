from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.enums import EstadoPago, UserRole
from app.models.finanzas import Factura, Pago, Presupuesto
from app.models.orden import OrdenServicio
from app.models.taller import Taller
from app.models.usuario import Usuario


def _generar_numero_factura(pago: Pago) -> str:
    prefijo = datetime.utcnow().strftime("FAC-%Y%m%d")
    return f"{prefijo}-{str(pago.id).split('-')[0].upper()}"


def obtener_factura(db: Session, factura_id) -> Factura | None:
    return db.execute(select(Factura).where(Factura.id == factura_id)).scalars().first()


def obtener_factura_por_orden(db: Session, orden_id) -> Factura | None:
    return db.execute(select(Factura).where(Factura.orden_id == orden_id)).scalars().first()


def listar_facturas_admin(
    db: Session,
    orden_id=None,
    pago_id=None,
    emitida_desde=None,
    emitida_hasta=None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(Factura)
    if orden_id is not None:
        query = query.where(Factura.orden_id == orden_id)
    if pago_id is not None:
        query = query.where(Factura.pago_id == pago_id)
    if emitida_desde is not None:
        query = query.where(Factura.emitida_en >= emitida_desde)
    if emitida_hasta is not None:
        query = query.where(Factura.emitida_en <= emitida_hasta)

    result = db.execute(query.order_by(Factura.emitida_en.desc()).offset(skip).limit(limit))
    return result.scalars().all()


def contar_facturas_admin(
    db: Session,
    orden_id=None,
    pago_id=None,
    emitida_desde=None,
    emitida_hasta=None,
) -> int:
    query = select(Factura)
    if orden_id is not None:
        query = query.where(Factura.orden_id == orden_id)
    if pago_id is not None:
        query = query.where(Factura.pago_id == pago_id)
    if emitida_desde is not None:
        query = query.where(Factura.emitida_en >= emitida_desde)
    if emitida_hasta is not None:
        query = query.where(Factura.emitida_en <= emitida_hasta)
    return len(db.execute(query).scalars().all())


def _obtener_orden_de_pago(db: Session, pago: Pago) -> OrdenServicio | None:
    return db.execute(select(OrdenServicio).where(OrdenServicio.id == pago.orden_id)).scalars().first()


def _es_conductor_dueno_orden(db: Session, orden: OrdenServicio, usuario_id) -> bool:
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    return bool(averia and averia.usuario_id == usuario_id)


def _es_taller_dueno_orden(db: Session, orden: OrdenServicio, usuario_id) -> bool:
    taller = db.execute(select(Taller).where(Taller.id == orden.taller_id)).scalars().first()
    return bool(taller and taller.usuario_id == usuario_id)


def validar_acceso_factura(db: Session, factura: Factura, usuario: Usuario) -> bool:
    if usuario.rol == UserRole.ADMIN:
        return True

    orden = db.execute(select(OrdenServicio).where(OrdenServicio.id == factura.orden_id)).scalars().first()
    if not orden:
        return False

    if usuario.rol == UserRole.CONDUCTOR:
        return _es_conductor_dueno_orden(db, orden, usuario.id)
    if usuario.rol == UserRole.TALLER:
        return _es_taller_dueno_orden(db, orden, usuario.id)
    return False


def crear_factura_para_pago(db: Session, pago_id, usuario_actual: Usuario) -> Factura:
    pago = db.execute(select(Pago).where(Pago.id == pago_id)).scalars().first()
    if not pago:
        raise ValueError("El pago no existe")

    orden = _obtener_orden_de_pago(db, pago)
    if not orden:
        raise ValueError("La orden asociada no existe")

    acceso = usuario_actual.rol == UserRole.ADMIN
    if usuario_actual.rol == UserRole.CONDUCTOR:
        acceso = _es_conductor_dueno_orden(db, orden, usuario_actual.id)
    elif usuario_actual.rol == UserRole.TALLER:
        acceso = _es_taller_dueno_orden(db, orden, usuario_actual.id)

    if not acceso:
        raise PermissionError("No tienes permisos para generar factura de este pago")

    if pago.estado != EstadoPago.COMPLETADO:
        raise ValueError("Solo se puede generar factura para un pago completado")

    factura_existente = db.execute(select(Factura).where(Factura.pago_id == pago.id)).scalars().first()
    if factura_existente:
        return factura_existente

    presupuesto = None
    if pago.presupuesto_id:
        presupuesto = db.execute(
            select(Presupuesto).where(Presupuesto.id == pago.presupuesto_id)
        ).scalars().first()

    taller = db.execute(select(Taller).where(Taller.id == orden.taller_id)).scalars().first()
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    conductor = (
        db.execute(select(Usuario).where(Usuario.id == averia.usuario_id)).scalars().first()
        if averia
        else None
    )

    subtotal = Decimal(str(pago.monto))
    impuesto = Decimal("0.00")
    total = subtotal + impuesto

    items = {
        "orden_id": str(orden.id),
        "presupuesto_id": str(presupuesto.id) if presupuesto else None,
        "detalle": presupuesto.items_detalle if presupuesto else {},
    }

    factura = Factura(
        pago_id=pago.id,
        orden_id=orden.id,
        numero_factura=_generar_numero_factura(pago),
        datos_emisor={
            "taller_id": str(taller.id) if taller else None,
            "nombre_taller": taller.nombre if taller else "Taller",
        },
        datos_receptor={
            "usuario_id": str(conductor.id) if conductor else None,
            "nombre": conductor.nombre if conductor else "Conductor",
            "apellido": conductor.apellido if conductor else "",
            "email": conductor.email if conductor else "",
        },
        items=items,
        subtotal=subtotal,
        impuesto=impuesto,
        total=total,
    )
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura
