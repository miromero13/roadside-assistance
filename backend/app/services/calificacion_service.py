from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.comunicacion import Calificacion
from app.models.enums import EstadoOrdenServicio, TipoCalificador, TipoNotificacion
from app.models.orden import OrdenServicio
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.services.notificacion_service import notificar_a_taller_por_orden


def _obtener_orden(db: Session, orden_id) -> OrdenServicio | None:
    return db.execute(select(OrdenServicio).where(OrdenServicio.id == orden_id)).scalars().first()


def _es_conductor_dueno_orden(db: Session, orden: OrdenServicio, conductor_id) -> bool:
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    return bool(averia and averia.usuario_id == conductor_id)


def _obtener_taller_de_orden(db: Session, orden: OrdenServicio) -> Taller | None:
    return db.execute(select(Taller).where(Taller.id == orden.taller_id)).scalars().first()


def _actualizar_promedio_taller(db: Session, taller: Taller) -> None:
    promedio = db.execute(
        select(func.avg(Calificacion.puntuacion)).where(
            Calificacion.calificado_id == taller.usuario_id,
            Calificacion.tipo_calificador == TipoCalificador.CONDUCTOR,
        )
    ).scalar_one_or_none()
    taller.calificacion_promedio = Decimal(str(round(float(promedio or 0), 2)))


def crear_calificacion_orden(
    db: Session,
    orden_id,
    conductor: Usuario,
    puntuacion: int,
    comentario: str | None,
) -> Calificacion:
    orden = _obtener_orden(db, orden_id)
    if not orden:
        raise ValueError("La orden no existe")

    if orden.estado != EstadoOrdenServicio.COMPLETADA:
        raise ValueError("Solo se puede calificar una orden completada")

    if not _es_conductor_dueno_orden(db, orden, conductor.id):
        raise PermissionError("No puedes calificar una orden que no te pertenece")

    existe = db.execute(
        select(Calificacion.id).where(
            Calificacion.orden_id == orden.id,
            Calificacion.calificador_id == conductor.id,
        )
    ).scalar_one_or_none()
    if existe:
        raise ValueError("Ya calificaste esta orden")

    taller = _obtener_taller_de_orden(db, orden)
    if not taller:
        raise ValueError("No se pudo identificar el taller de la orden")

    calificacion = Calificacion(
        orden_id=orden.id,
        calificador_id=conductor.id,
        calificado_id=taller.usuario_id,
        tipo_calificador=TipoCalificador.CONDUCTOR,
        puntuacion=puntuacion,
        comentario=comentario,
    )
    db.add(calificacion)

    _actualizar_promedio_taller(db, taller)
    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.CALIFICACION_RECIBIDA,
        "Nueva calificación recibida",
        "El conductor calificó el servicio de la orden completada.",
    )

    db.commit()
    db.refresh(calificacion)
    return calificacion


def listar_calificaciones_orden(db: Session, orden_id):
    return (
        db.execute(
            select(Calificacion)
            .where(Calificacion.orden_id == orden_id)
            .order_by(Calificacion.creado_en.desc())
        )
        .scalars()
        .all()
    )
