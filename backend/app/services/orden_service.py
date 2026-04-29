import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.enums import EstadoOrdenServicio, TipoNotificacion, UserRole
from app.models.orden import AsignacionOrden, HistorialEstadoOrden, OrdenServicio
from app.models.taller import CategoriaServicio, Mecanico, ServicioTaller, Taller
from app.models.enums import EstadoAsignacion
from app.models.usuario import Usuario
from app.schemas.orden_schema import OrdenCrearPorSeleccionManual
from app.services.metrica_service import recalcular_metrica_orden
from app.services.notificacion_service import (
    notificar_a_conductor_por_orden,
    notificar_a_mecanicos_activos_por_orden,
    notificar_a_taller_por_orden,
)
from app.services.taller_disponibilidad_service import calcular_distancia_km

logger = logging.getLogger(__name__)


ESTADOS_ORDEN_ACTIVOS = {
    EstadoOrdenServicio.PENDIENTE_RESPUESTA,
    EstadoOrdenServicio.ACEPTADA,
    EstadoOrdenServicio.TECNICO_ASIGNADO,
    EstadoOrdenServicio.EN_CAMINO,
    EstadoOrdenServicio.EN_PROCESO,
}

ESTADOS_PERMITIDOS_ASIGNACION_TALLER = {
    EstadoOrdenServicio.ACEPTADA,
    EstadoOrdenServicio.TECNICO_ASIGNADO,
    EstadoOrdenServicio.EN_CAMINO,
    EstadoOrdenServicio.EN_PROCESO,
}

ESTADOS_ORDEN_CANCELABLES = {
    EstadoOrdenServicio.PENDIENTE_RESPUESTA,
    EstadoOrdenServicio.ACEPTADA,
    EstadoOrdenServicio.TECNICO_ASIGNADO,
    EstadoOrdenServicio.EN_CAMINO,
    EstadoOrdenServicio.EN_PROCESO,
}

ESTADOS_ORDEN_COMPLETABLES = {
    EstadoOrdenServicio.EN_PROCESO,
    EstadoOrdenServicio.EN_CAMINO,
    EstadoOrdenServicio.TECNICO_ASIGNADO,
}


def _registrar_historial_orden(
    db: Session,
    orden: OrdenServicio,
    estado_anterior: EstadoOrdenServicio | None,
    estado_nuevo: EstadoOrdenServicio,
    usuario_id,
    observacion: str | None = None,
) -> None:
    historial = HistorialEstadoOrden(
        orden_id=orden.id,
        estado_anterior=estado_anterior.value if estado_anterior else None,
        estado_nuevo=estado_nuevo.value,
        usuario_id=usuario_id,
        observacion=observacion,
    )
    db.add(historial)


def crear_orden_por_seleccion_manual(
    db: Session,
    payload: OrdenCrearPorSeleccionManual,
    conductor: Usuario,
) -> OrdenServicio:
    averia = db.execute(select(Averia).where(Averia.id == payload.averia_id)).scalars().first()
    if not averia:
        raise ValueError("La avería no existe")
    if averia.usuario_id != conductor.id:
        raise PermissionError("No puedes crear una orden sobre una avería que no te pertenece")

    orden_activa = db.execute(
        select(OrdenServicio)
        .where(
            OrdenServicio.averia_id == payload.averia_id,
            OrdenServicio.estado.in_(ESTADOS_ORDEN_ACTIVOS),
        )
        .limit(1)
    ).scalars().first()
    if orden_activa:
        raise ValueError("La avería ya tiene una orden activa")

    taller = db.execute(select(Taller).where(Taller.id == payload.taller_id)).scalars().first()
    if not taller or not taller.activo:
        raise ValueError("El taller seleccionado no está disponible")

    categoria = db.execute(
        select(CategoriaServicio).where(CategoriaServicio.id == payload.categoria_id)
    ).scalars().first()
    if not categoria or not categoria.activo:
        raise ValueError("La categoría seleccionada no está disponible")

    servicio_relacion = db.execute(
        select(ServicioTaller).where(
            ServicioTaller.taller_id == taller.id,
            ServicioTaller.categoria_id == payload.categoria_id,
            ServicioTaller.activo.is_(True),
        )
    ).scalars().first()
    if not servicio_relacion:
        raise ValueError("El taller no ofrece la categoría seleccionada")

    distancia = calcular_distancia_km(
        float(averia.latitud_averia),
        float(averia.longitud_averia),
        float(taller.latitud),
        float(taller.longitud),
    )
    if distancia > float(taller.radio_cobertura_km):
        raise ValueError("El taller seleccionado está fuera de cobertura")

    orden = OrdenServicio(
        averia_id=payload.averia_id,
        taller_id=payload.taller_id,
        categoria_id=payload.categoria_id,
        estado=EstadoOrdenServicio.PENDIENTE_RESPUESTA,
        es_domicilio=payload.es_domicilio,
        notas_conductor=payload.notas_conductor,
    )
    db.add(orden)
    db.flush()

    _registrar_historial_orden(
        db,
        orden,
        None,
        EstadoOrdenServicio.PENDIENTE_RESPUESTA,
        conductor.id,
        observacion="Orden creada por selección manual de taller",
    )
    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_NUEVA,
        "Nueva orden",
        "Se recibió una nueva solicitud de asistencia para tu taller.",
    )
    logger.info("Orden creada y notificada a taller orden_id=%s taller_id=%s", orden.id, orden.taller_id)
    db.commit()
    db.refresh(orden)
    return orden


def obtener_taller_por_usuario(db: Session, usuario_taller_id) -> Taller | None:
    return db.execute(select(Taller).where(Taller.usuario_id == usuario_taller_id)).scalars().first()


def aceptar_orden_por_taller(
    db: Session,
    orden: OrdenServicio,
    taller: Taller,
    usuario_taller: Usuario,
    tiempo_estimado_respuesta_min: int,
    tiempo_estimado_llegada_min: int | None = None,
    notas_taller: str | None = None,
) -> OrdenServicio:
    if orden.taller_id != taller.id:
        raise PermissionError("No puedes aceptar órdenes de otro taller")
    if orden.estado != EstadoOrdenServicio.PENDIENTE_RESPUESTA:
        raise ValueError("Solo se pueden aceptar órdenes en estado pendiente_respuesta")

    estado_anterior = orden.estado
    orden.estado = EstadoOrdenServicio.ACEPTADA
    orden.respondido_en = datetime.utcnow()
    orden.aceptado_en = datetime.utcnow()
    orden.tiempo_estimado_respuesta_min = tiempo_estimado_respuesta_min
    orden.tiempo_estimado_llegada_min = tiempo_estimado_llegada_min
    if notas_taller is not None:
        orden.notas_taller = notas_taller

    _registrar_historial_orden(
        db,
        orden,
        estado_anterior,
        EstadoOrdenServicio.ACEPTADA,
        usuario_taller.id,
        observacion="Orden aceptada por taller",
    )
    notificar_a_conductor_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACEPTADA,
        "Orden aceptada",
        "El taller acepto tu solicitud de asistencia.",
    )
    logger.info(
        "Orden aceptada y notificacion generada orden_id=%s conductor_id=%s taller_id=%s",
        orden.id,
        orden.averia.usuario_id if orden.averia else None,
        orden.taller_id,
    )
    db.commit()
    db.refresh(orden)
    return orden


def rechazar_orden_por_taller(
    db: Session,
    orden: OrdenServicio,
    taller: Taller,
    usuario_taller: Usuario,
    motivo_rechazo: str,
) -> OrdenServicio:
    if orden.taller_id != taller.id:
        raise PermissionError("No puedes rechazar órdenes de otro taller")
    if orden.estado != EstadoOrdenServicio.PENDIENTE_RESPUESTA:
        raise ValueError("Solo se pueden rechazar órdenes en estado pendiente_respuesta")

    estado_anterior = orden.estado
    orden.estado = EstadoOrdenServicio.RECHAZADA
    orden.respondido_en = datetime.utcnow()
    orden.rechazado_en = datetime.utcnow()
    orden.motivo_rechazo = motivo_rechazo

    _registrar_historial_orden(
        db,
        orden,
        estado_anterior,
        EstadoOrdenServicio.RECHAZADA,
        usuario_taller.id,
        observacion="Orden rechazada por taller",
    )
    notificar_a_conductor_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_RECHAZADA,
        "Orden rechazada",
        "El taller rechazo tu solicitud de asistencia.",
    )

    db.flush()
    _crear_orden_automatica_tras_rechazo(db, orden, usuario_taller)

    db.commit()
    db.refresh(orden)
    return orden


def _crear_orden_automatica_tras_rechazo(
    db: Session,
    orden_rechazada: OrdenServicio,
    usuario_taller: Usuario,
) -> OrdenServicio | None:
    averia = db.execute(select(Averia).where(Averia.id == orden_rechazada.averia_id)).scalars().first()
    if not averia:
        return None

    orden_activa = db.execute(
        select(OrdenServicio)
        .where(
            OrdenServicio.averia_id == orden_rechazada.averia_id,
            OrdenServicio.estado.in_(ESTADOS_ORDEN_ACTIVOS),
        )
        .limit(1)
    ).scalars().first()
    if orden_activa:
        return None

    talleres_intentados = set(
        db.execute(
            select(OrdenServicio.taller_id).where(OrdenServicio.averia_id == orden_rechazada.averia_id)
        )
        .scalars()
        .all()
    )

    servicios_query = select(ServicioTaller).where(
        ServicioTaller.categoria_id == orden_rechazada.categoria_id,
        ServicioTaller.activo.is_(True),
    )
    if talleres_intentados:
        servicios_query = servicios_query.where(ServicioTaller.taller_id.notin_(list(talleres_intentados)))

    servicios = db.execute(servicios_query).scalars().all()

    mejor_taller: Taller | None = None
    mejor_distancia: float | None = None
    for servicio in servicios:
        taller = db.execute(
            select(Taller).where(Taller.id == servicio.taller_id, Taller.activo.is_(True))
        ).scalars().first()
        if not taller:
            continue

        distancia = calcular_distancia_km(
            float(averia.latitud_averia),
            float(averia.longitud_averia),
            float(taller.latitud),
            float(taller.longitud),
        )
        if distancia > float(taller.radio_cobertura_km):
            continue

        if mejor_distancia is None or distancia < mejor_distancia:
            mejor_taller = taller
            mejor_distancia = distancia

    if not mejor_taller:
        return None

    nueva_orden = OrdenServicio(
        averia_id=orden_rechazada.averia_id,
        taller_id=mejor_taller.id,
        categoria_id=orden_rechazada.categoria_id,
        estado=EstadoOrdenServicio.PENDIENTE_RESPUESTA,
        es_domicilio=orden_rechazada.es_domicilio,
        notas_conductor=orden_rechazada.notas_conductor,
    )
    db.add(nueva_orden)
    db.flush()

    _registrar_historial_orden(
        db,
        nueva_orden,
        None,
        EstadoOrdenServicio.PENDIENTE_RESPUESTA,
        usuario_taller.id,
        observacion="Orden creada automáticamente tras rechazo del taller anterior",
    )

    notificar_a_taller_por_orden(
        db,
        nueva_orden,
        TipoNotificacion.ORDEN_NUEVA,
        "Nueva orden",
        "Se asignó automáticamente una nueva solicitud de asistencia.",
    )
    notificar_a_conductor_por_orden(
        db,
        nueva_orden,
        TipoNotificacion.ORDEN_NUEVA,
        "Nueva opción de taller encontrada",
        "Tu solicitud fue redirigida automáticamente a otro taller compatible.",
    )
    return nueva_orden


def _obtener_asignacion_activa(db: Session, orden_id) -> AsignacionOrden | None:
    return (
        db.execute(
            select(AsignacionOrden)
            .where(
                AsignacionOrden.orden_id == orden_id,
                AsignacionOrden.estado.in_(
                    {
                        EstadoAsignacion.ASIGNADO,
                        EstadoAsignacion.EN_CAMINO,
                        EstadoAsignacion.ATENDIENDO,
                    }
                ),
            )
            .order_by(AsignacionOrden.asignado_en.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )


def asignar_mecanico_a_orden(
    db: Session,
    orden: OrdenServicio,
    taller: Taller,
    usuario_taller: Usuario,
    mecanico_id,
    notas: str | None = None,
) -> AsignacionOrden:
    if orden.taller_id != taller.id:
        raise PermissionError("No puedes asignar mecánicos a órdenes de otro taller")
    if orden.estado not in ESTADOS_PERMITIDOS_ASIGNACION_TALLER:
        raise ValueError("La orden no está en un estado válido para asignar mecánico")

    mecanico = db.execute(
        select(Mecanico).where(Mecanico.id == mecanico_id, Mecanico.taller_id == taller.id)
    ).scalars().first()
    if not mecanico:
        raise ValueError("El mecánico no pertenece al taller")
    if not mecanico.activo or not mecanico.disponible:
        raise ValueError("El mecánico seleccionado no está disponible")

    asignacion_activa = _obtener_asignacion_activa(db, orden.id)
    if asignacion_activa:
        asignacion_activa.estado = EstadoAsignacion.CANCELADO
        asignacion_activa.finalizado_en = datetime.utcnow()
        if notas:
            asignacion_activa.notas = (
                f"{asignacion_activa.notas or ''} | Reasignado: {notas}".strip(" |")
            )
        else:
            asignacion_activa.notas = (
                f"{asignacion_activa.notas or ''} | Reasignado por taller".strip(" |")
            )
        mecanico_anterior = db.execute(
            select(Mecanico).where(Mecanico.id == asignacion_activa.mecanico_id)
        ).scalars().first()
        if mecanico_anterior:
            mecanico_anterior.disponible = True

    nueva_asignacion = AsignacionOrden(
        orden_id=orden.id,
        mecanico_id=mecanico.id,
        asignado_por=usuario_taller.id,
        estado=EstadoAsignacion.ASIGNADO,
        notas=notas,
    )
    db.add(nueva_asignacion)
    db.flush()
    mecanico.disponible = False

    estado_anterior = orden.estado
    orden.estado = EstadoOrdenServicio.TECNICO_ASIGNADO
    _registrar_historial_orden(
        db,
        orden,
        estado_anterior,
        EstadoOrdenServicio.TECNICO_ASIGNADO,
        usuario_taller.id,
        observacion="Mecánico asignado a la orden",
    )
    notificar_a_conductor_por_orden(
        db,
        orden,
        TipoNotificacion.TECNICO_ASIGNADO,
        "Tecnico asignado",
        "Un mecanico fue asignado a tu orden.",
    )
    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.TECNICO_ASIGNADO,
        "Tecnico asignado",
        "Se asigno un mecanico a la orden.",
    )
    notificar_a_mecanicos_activos_por_orden(
        db,
        orden,
        TipoNotificacion.TECNICO_ASIGNADO,
        "Orden asignada",
        "Tienes una nueva orden asignada.",
    )

    db.commit()
    db.refresh(nueva_asignacion)
    return nueva_asignacion


def listar_ordenes_para_usuario(
    db: Session,
    usuario: Usuario,
    estado: EstadoOrdenServicio | None = None,
):
    if usuario.rol == UserRole.ADMIN:
        query = select(OrdenServicio)
        if estado is not None:
            query = query.where(OrdenServicio.estado == estado)
        result = db.execute(query.order_by(OrdenServicio.creado_en.desc()))
        return result.scalars().all()

    if usuario.rol == UserRole.CONDUCTOR:
        query = (
            select(OrdenServicio)
            .join(Averia, Averia.id == OrdenServicio.averia_id)
            .where(Averia.usuario_id == usuario.id)
        )
        if estado is not None:
            query = query.where(OrdenServicio.estado == estado)
        result = db.execute(query.order_by(OrdenServicio.creado_en.desc()))
        return result.scalars().all()

    if usuario.rol == UserRole.TALLER:
        taller = db.execute(select(Taller).where(Taller.usuario_id == usuario.id)).scalars().first()
        if not taller:
            return []
        query = select(OrdenServicio).where(OrdenServicio.taller_id == taller.id)
        if estado is not None:
            query = query.where(OrdenServicio.estado == estado)
        result = db.execute(query.order_by(OrdenServicio.creado_en.desc()))
        return result.scalars().all()

    if usuario.rol == UserRole.MECANICO:
        query = (
            select(OrdenServicio)
            .join(AsignacionOrden, AsignacionOrden.orden_id == OrdenServicio.id)
            .join(Mecanico, Mecanico.id == AsignacionOrden.mecanico_id)
            .where(Mecanico.usuario_id == usuario.id)
            .distinct()
        )
        if estado is not None:
            query = query.where(OrdenServicio.estado == estado)
        result = db.execute(query.order_by(OrdenServicio.creado_en.desc()))
        return result.scalars().all()

    return []


def obtener_orden(db: Session, orden_id) -> OrdenServicio | None:
    result = db.execute(select(OrdenServicio).where(OrdenServicio.id == orden_id))
    return result.scalars().first()


def listar_historial_estados_orden(db: Session, orden_id):
    return (
        db.execute(
            select(HistorialEstadoOrden)
            .where(HistorialEstadoOrden.orden_id == orden_id)
            .order_by(HistorialEstadoOrden.creado_en.asc())
        )
        .scalars()
        .all()
    )


def listar_asignaciones_orden(db: Session, orden_id):
    return (
        db.execute(
            select(AsignacionOrden)
            .where(AsignacionOrden.orden_id == orden_id)
            .order_by(AsignacionOrden.asignado_en.desc())
        )
        .scalars()
        .all()
    )


def cancelar_orden(
    db: Session,
    orden: OrdenServicio,
    usuario_actual: Usuario,
    motivo_cancelacion: str,
) -> OrdenServicio:
    if orden.estado not in ESTADOS_ORDEN_CANCELABLES:
        raise ValueError("La orden no se puede cancelar en su estado actual")

    if not validar_acceso_orden(db, orden, usuario_actual) and usuario_actual.rol != UserRole.ADMIN:
        raise PermissionError("No tienes permisos para cancelar esta orden")

    estado_anterior = orden.estado
    orden.estado = EstadoOrdenServicio.CANCELADA
    orden.motivo_cancelacion = motivo_cancelacion
    orden.cancelado_en = datetime.utcnow()

    asignaciones = listar_asignaciones_orden(db, orden.id)
    for asignacion in asignaciones:
        if asignacion.estado in {
            EstadoAsignacion.ASIGNADO,
            EstadoAsignacion.EN_CAMINO,
            EstadoAsignacion.ATENDIENDO,
        }:
            asignacion.estado = EstadoAsignacion.CANCELADO
            asignacion.finalizado_en = datetime.utcnow()
            mecanico = db.execute(
                select(Mecanico).where(Mecanico.id == asignacion.mecanico_id)
            ).scalars().first()
            if mecanico:
                mecanico.disponible = True

    _registrar_historial_orden(
        db,
        orden,
        estado_anterior,
        EstadoOrdenServicio.CANCELADA,
        usuario_actual.id,
        observacion=motivo_cancelacion,
    )
    notificar_a_conductor_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACTUALIZADA,
        "Orden cancelada",
        "Tu orden fue cancelada.",
    )
    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACTUALIZADA,
        "Orden cancelada",
        "La orden fue cancelada.",
    )
    notificar_a_mecanicos_activos_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACTUALIZADA,
        "Orden cancelada",
        "La orden fue cancelada.",
    )
    db.commit()
    db.refresh(orden)
    return orden


def completar_orden_manual(
    db: Session,
    orden: OrdenServicio,
    usuario_actual: Usuario,
    observacion: str | None = None,
) -> OrdenServicio:
    if orden.estado not in ESTADOS_ORDEN_COMPLETABLES:
        raise ValueError("La orden no se puede completar manualmente en su estado actual")

    if usuario_actual.rol == UserRole.TALLER:
        taller = obtener_taller_por_usuario(db, usuario_actual.id)
        if not taller or taller.id != orden.taller_id:
            raise PermissionError("No puedes completar órdenes de otro taller")
    elif usuario_actual.rol != UserRole.ADMIN:
        raise PermissionError("No tienes permisos para completar esta orden")

    estado_anterior = orden.estado
    orden.estado = EstadoOrdenServicio.COMPLETADA
    orden.completado_en = datetime.utcnow()

    asignaciones = listar_asignaciones_orden(db, orden.id)
    for asignacion in asignaciones:
        if asignacion.estado in {
            EstadoAsignacion.ASIGNADO,
            EstadoAsignacion.EN_CAMINO,
            EstadoAsignacion.ATENDIENDO,
        }:
            asignacion.estado = EstadoAsignacion.FINALIZADO
            asignacion.finalizado_en = datetime.utcnow()
            mecanico = db.execute(
                select(Mecanico).where(Mecanico.id == asignacion.mecanico_id)
            ).scalars().first()
            if mecanico:
                mecanico.disponible = True

    _registrar_historial_orden(
        db,
        orden,
        estado_anterior,
        EstadoOrdenServicio.COMPLETADA,
        usuario_actual.id,
        observacion=observacion or "Orden completada manualmente",
    )
    notificar_a_conductor_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACTUALIZADA,
        "Orden completada",
        "Tu orden fue marcada como completada.",
    )
    notificar_a_taller_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACTUALIZADA,
        "Orden completada",
        "La orden fue marcada como completada.",
    )
    notificar_a_mecanicos_activos_por_orden(
        db,
        orden,
        TipoNotificacion.ORDEN_ACTUALIZADA,
        "Orden completada",
        "La orden fue marcada como completada.",
    )
    recalcular_metrica_orden(db, orden)
    db.commit()
    db.refresh(orden)
    return orden


def validar_acceso_orden(db: Session, orden: OrdenServicio, usuario: Usuario) -> bool:
    if usuario.rol == UserRole.ADMIN:
        return True

    if usuario.rol == UserRole.CONDUCTOR:
        averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
        return bool(averia and averia.usuario_id == usuario.id)

    if usuario.rol == UserRole.TALLER:
        taller = db.execute(select(Taller).where(Taller.usuario_id == usuario.id)).scalars().first()
        return bool(taller and orden.taller_id == taller.id)

    if usuario.rol == UserRole.MECANICO:
        asignacion = db.execute(
            select(AsignacionOrden)
            .join(Mecanico, Mecanico.id == AsignacionOrden.mecanico_id)
            .where(
                AsignacionOrden.orden_id == orden.id,
                Mecanico.usuario_id == usuario.id,
            )
            .limit(1)
        ).scalars().first()
        return asignacion is not None

    return False
