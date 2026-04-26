from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EstadoAsignacion, EstadoOrdenServicio, EstadoPresupuesto, TipoNotificacion
from app.models.finanzas import Presupuesto
from app.models.orden import AsignacionOrden, OrdenServicio
from app.models.taller import Mecanico
from app.models.usuario import Usuario
from app.services.notificacion_service import notificar_a_conductor_por_orden
from app.services.orden_service import _registrar_historial_orden


TRANSICIONES_ASIGNACION_VALIDAS = {
    EstadoAsignacion.ASIGNADO: {EstadoAsignacion.EN_CAMINO, EstadoAsignacion.CANCELADO},
    EstadoAsignacion.EN_CAMINO: {EstadoAsignacion.ATENDIENDO, EstadoAsignacion.CANCELADO},
    EstadoAsignacion.ATENDIENDO: {EstadoAsignacion.FINALIZADO, EstadoAsignacion.CANCELADO},
    EstadoAsignacion.FINALIZADO: set(),
    EstadoAsignacion.CANCELADO: set(),
}


def obtener_asignacion(db: Session, asignacion_id) -> AsignacionOrden | None:
    return db.execute(select(AsignacionOrden).where(AsignacionOrden.id == asignacion_id)).scalars().first()


def obtener_mecanico_por_usuario(db: Session, usuario_id) -> Mecanico | None:
    return db.execute(select(Mecanico).where(Mecanico.usuario_id == usuario_id)).scalars().first()


def listar_asignaciones_mecanico(db: Session, mecanico_id):
    return (
        db.execute(
            select(AsignacionOrden)
            .where(AsignacionOrden.mecanico_id == mecanico_id)
            .order_by(AsignacionOrden.asignado_en.desc())
        )
        .scalars()
        .all()
    )


def _orden_tiene_presupuesto_aprobado(db: Session, orden_id) -> bool:
    presupuesto = db.execute(
        select(Presupuesto.id).where(
            Presupuesto.orden_id == orden_id,
            Presupuesto.estado == EstadoPresupuesto.APROBADO,
        )
    ).scalar_one_or_none()
    return presupuesto is not None


def actualizar_estado_asignacion(
    db: Session,
    asignacion: AsignacionOrden,
    mecanico: Mecanico,
    usuario_mecanico: Usuario,
    nuevo_estado: EstadoAsignacion,
    notas: str | None = None,
) -> AsignacionOrden:
    if asignacion.mecanico_id != mecanico.id:
        raise PermissionError("No puedes actualizar una asignación que no te pertenece")

    estado_actual = asignacion.estado
    permitidos = TRANSICIONES_ASIGNACION_VALIDAS.get(estado_actual, set())
    if nuevo_estado not in permitidos:
        raise ValueError(
            f"Transición inválida de asignación: {estado_actual.value} -> {nuevo_estado.value}"
        )

    orden = db.execute(select(OrdenServicio).where(OrdenServicio.id == asignacion.orden_id)).scalars().first()
    if not orden:
        raise ValueError("La orden asociada no existe")

    asignacion.estado = nuevo_estado
    if notas is not None:
        asignacion.notas = notas

    if nuevo_estado == EstadoAsignacion.EN_CAMINO:
        asignacion.salida_en = datetime.utcnow()
        if orden.estado != EstadoOrdenServicio.EN_CAMINO:
            estado_anterior = orden.estado
            orden.estado = EstadoOrdenServicio.EN_CAMINO
            _registrar_historial_orden(
                db,
                orden,
                estado_anterior,
                EstadoOrdenServicio.EN_CAMINO,
                usuario_mecanico.id,
                observacion="Mecánico en camino",
            )
            notificar_a_conductor_por_orden(
                db,
                orden,
                TipoNotificacion.TECNICO_EN_CAMINO,
                "Tecnico en camino",
                "Tu mecanico ya va en camino al lugar de la averia.",
            )

    elif nuevo_estado == EstadoAsignacion.ATENDIENDO:
        if not _orden_tiene_presupuesto_aprobado(db, orden.id):
            raise ValueError("No se puede iniciar atención sin presupuesto aprobado")
        asignacion.llegada_en = datetime.utcnow()
        if orden.estado != EstadoOrdenServicio.EN_PROCESO:
            estado_anterior = orden.estado
            orden.estado = EstadoOrdenServicio.EN_PROCESO
            if orden.iniciado_en is None:
                orden.iniciado_en = datetime.utcnow()
            _registrar_historial_orden(
                db,
                orden,
                estado_anterior,
                EstadoOrdenServicio.EN_PROCESO,
                usuario_mecanico.id,
                observacion="Mecánico atendiendo la orden",
            )

    elif nuevo_estado in {EstadoAsignacion.FINALIZADO, EstadoAsignacion.CANCELADO}:
        asignacion.finalizado_en = datetime.utcnow()
        mecanico.disponible = True
        if nuevo_estado == EstadoAsignacion.CANCELADO and orden.estado == EstadoOrdenServicio.EN_CAMINO:
            estado_anterior = orden.estado
            orden.estado = EstadoOrdenServicio.ACEPTADA
            _registrar_historial_orden(
                db,
                orden,
                estado_anterior,
                EstadoOrdenServicio.ACEPTADA,
                usuario_mecanico.id,
                observacion="Asignación cancelada por mecánico",
            )

    db.commit()
    db.refresh(asignacion)
    return asignacion
