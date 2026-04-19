from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.comunicacion import Notificacion
from app.models.enums import TipoNotificacion
from app.models.orden import OrdenServicio
from app.models.taller import Taller


def crear_notificacion(
    db: Session,
    usuario_id,
    tipo: TipoNotificacion,
    titulo: str,
    mensaje: str,
    orden_id=None,
) -> Notificacion:
    notificacion = Notificacion(
        usuario_id=usuario_id,
        orden_id=orden_id,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo,
    )
    db.add(notificacion)
    return notificacion


def _obtener_conductor_y_taller_usuario_ids(db: Session, orden: OrdenServicio):
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    taller = db.execute(select(Taller).where(Taller.id == orden.taller_id)).scalars().first()
    conductor_id = averia.usuario_id if averia else None
    taller_usuario_id = taller.usuario_id if taller else None
    return conductor_id, taller_usuario_id


def notificar_a_conductor_por_orden(
    db: Session,
    orden: OrdenServicio,
    tipo: TipoNotificacion,
    titulo: str,
    mensaje: str,
) -> None:
    conductor_id, _ = _obtener_conductor_y_taller_usuario_ids(db, orden)
    if conductor_id:
        crear_notificacion(db, conductor_id, tipo, titulo, mensaje, orden_id=orden.id)


def notificar_a_taller_por_orden(
    db: Session,
    orden: OrdenServicio,
    tipo: TipoNotificacion,
    titulo: str,
    mensaje: str,
) -> None:
    _, taller_usuario_id = _obtener_conductor_y_taller_usuario_ids(db, orden)
    if taller_usuario_id:
        crear_notificacion(db, taller_usuario_id, tipo, titulo, mensaje, orden_id=orden.id)


def notificar_a_conductor_y_taller_por_orden(
    db: Session,
    orden: OrdenServicio,
    tipo: TipoNotificacion,
    titulo: str,
    mensaje: str,
) -> None:
    conductor_id, taller_usuario_id = _obtener_conductor_y_taller_usuario_ids(db, orden)
    if conductor_id:
        crear_notificacion(db, conductor_id, tipo, titulo, mensaje, orden_id=orden.id)
    if taller_usuario_id:
        crear_notificacion(db, taller_usuario_id, tipo, titulo, mensaje, orden_id=orden.id)


def listar_notificaciones_usuario(
    db: Session,
    usuario_id,
    skip: int = 0,
    limit: int = 20,
    solo_no_leidas: bool = False,
):
    query = select(Notificacion).where(Notificacion.usuario_id == usuario_id)
    if solo_no_leidas:
        query = query.where(Notificacion.leida.is_(False))
    result = db.execute(
        query.order_by(Notificacion.creado_en.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


def contar_notificaciones_usuario(db: Session, usuario_id, solo_no_leidas: bool = False) -> int:
    query = select(Notificacion).where(Notificacion.usuario_id == usuario_id)
    if solo_no_leidas:
        query = query.where(Notificacion.leida.is_(False))
    return len(db.execute(query).scalars().all())


def obtener_notificacion_de_usuario(db: Session, notificacion_id, usuario_id) -> Notificacion | None:
    return (
        db.execute(
            select(Notificacion).where(
                Notificacion.id == notificacion_id,
                Notificacion.usuario_id == usuario_id,
            )
        )
        .scalars()
        .first()
    )


def marcar_notificacion_leida(db: Session, notificacion: Notificacion) -> Notificacion:
    if not notificacion.leida:
        notificacion.leida = True
        db.commit()
        db.refresh(notificacion)
    return notificacion


def marcar_todas_leidas_usuario(db: Session, usuario_id) -> int:
    notificaciones = db.execute(
        select(Notificacion).where(
            Notificacion.usuario_id == usuario_id,
            Notificacion.leida.is_(False),
        )
    ).scalars().all()

    for item in notificaciones:
        item.leida = True

    db.commit()
    return len(notificaciones)
