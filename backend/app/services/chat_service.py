from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.comunicacion import Chat, Mensaje
from app.models.enums import EstadoAsignacion, EstadoOrdenServicio, TipoMensaje, TipoNotificacion, UserRole
from app.models.orden import AsignacionOrden, OrdenServicio
from app.models.taller import Mecanico, Taller
from app.models.usuario import Usuario
from app.services.notificacion_service import crear_notificacion


ESTADOS_CHAT_HABILITADO = {
    EstadoOrdenServicio.ACEPTADA,
    EstadoOrdenServicio.TECNICO_ASIGNADO,
    EstadoOrdenServicio.EN_CAMINO,
    EstadoOrdenServicio.EN_PROCESO,
    EstadoOrdenServicio.COMPLETADA,
}

ESTADOS_ASIGNACION_ACTIVA = {
    EstadoAsignacion.ASIGNADO,
    EstadoAsignacion.EN_CAMINO,
    EstadoAsignacion.ATENDIENDO,
}


def obtener_orden(db: Session, orden_id) -> OrdenServicio | None:
    return db.execute(select(OrdenServicio).where(OrdenServicio.id == orden_id)).scalars().first()


def obtener_chat_por_orden(db: Session, orden_id) -> Chat | None:
    return db.execute(select(Chat).where(Chat.orden_id == orden_id)).scalars().first()


def obtener_chat(db: Session, chat_id) -> Chat | None:
    return db.execute(select(Chat).where(Chat.id == chat_id)).scalars().first()


def _obtener_conductor_id(db: Session, orden: OrdenServicio):
    averia = db.execute(select(Averia).where(Averia.id == orden.averia_id)).scalars().first()
    return averia.usuario_id if averia else None


def _obtener_taller_usuario_id(db: Session, orden: OrdenServicio):
    taller = db.execute(select(Taller).where(Taller.id == orden.taller_id)).scalars().first()
    return taller.usuario_id if taller else None


def _obtener_mecanico_usuario_ids_activos(db: Session, orden_id) -> list:
    result = db.execute(
        select(Mecanico.usuario_id)
        .join(AsignacionOrden, AsignacionOrden.mecanico_id == Mecanico.id)
        .where(
            AsignacionOrden.orden_id == orden_id,
            AsignacionOrden.estado.in_(ESTADOS_ASIGNACION_ACTIVA),
        )
    )
    return [item[0] for item in result.all()]


def validar_acceso_chat(db: Session, orden: OrdenServicio, usuario: Usuario) -> bool:
    if usuario.rol == UserRole.ADMIN:
        return True

    conductor_id = _obtener_conductor_id(db, orden)
    if usuario.rol == UserRole.CONDUCTOR:
        return bool(conductor_id and conductor_id == usuario.id)

    taller_usuario_id = _obtener_taller_usuario_id(db, orden)
    if usuario.rol == UserRole.TALLER:
        return bool(taller_usuario_id and taller_usuario_id == usuario.id)

    if usuario.rol == UserRole.MECANICO:
        mecanico_usuario_ids = _obtener_mecanico_usuario_ids_activos(db, orden.id)
        return usuario.id in mecanico_usuario_ids

    return False


def obtener_o_crear_chat_por_orden(db: Session, orden: OrdenServicio, usuario: Usuario) -> Chat:
    if orden.estado not in ESTADOS_CHAT_HABILITADO:
        raise ValueError("El chat no está habilitado para el estado actual de la orden")

    if not validar_acceso_chat(db, orden, usuario):
        raise PermissionError("No tienes permisos para acceder al chat de esta orden")

    chat = obtener_chat_por_orden(db, orden.id)
    if chat:
        return chat

    chat = Chat(orden_id=orden.id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def listar_mensajes_chat(db: Session, chat_id, skip: int = 0, limit: int = 50):
    result = db.execute(
        select(Mensaje)
        .where(Mensaje.chat_id == chat_id)
        .order_by(Mensaje.enviado_en.asc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


def contar_mensajes_chat(db: Session, chat_id) -> int:
    result = db.execute(select(Mensaje.id).where(Mensaje.chat_id == chat_id))
    return len(result.scalars().all())


def _destinatarios_chat(db: Session, orden: OrdenServicio, remitente_id) -> list:
    destinatarios = set()

    conductor_id = _obtener_conductor_id(db, orden)
    if conductor_id:
        destinatarios.add(conductor_id)

    taller_usuario_id = _obtener_taller_usuario_id(db, orden)
    if taller_usuario_id:
        destinatarios.add(taller_usuario_id)

    for usuario_id in _obtener_mecanico_usuario_ids_activos(db, orden.id):
        destinatarios.add(usuario_id)

    destinatarios.discard(remitente_id)
    return list(destinatarios)


def enviar_mensaje(
    db: Session,
    chat: Chat,
    orden: OrdenServicio,
    remitente: Usuario,
    contenido: str | None,
    tipo: TipoMensaje,
    media_url: str | None,
) -> Mensaje:
    if not validar_acceso_chat(db, orden, remitente):
        raise PermissionError("No tienes permisos para enviar mensajes en este chat")

    if tipo == TipoMensaje.TEXTO and not contenido:
        raise ValueError("El contenido es obligatorio para mensajes de texto")
    if tipo in {TipoMensaje.IMAGEN, TipoMensaje.AUDIO} and not media_url:
        raise ValueError("La media_url es obligatoria para mensajes multimedia")

    mensaje = Mensaje(
        chat_id=chat.id,
        remitente_id=remitente.id,
        contenido=contenido,
        tipo=tipo,
        media_url=media_url,
    )
    db.add(mensaje)

    for usuario_destino in _destinatarios_chat(db, orden, remitente.id):
        crear_notificacion(
            db,
            usuario_destino,
            TipoNotificacion.MENSAJE_NUEVO,
            "Nuevo mensaje",
            "Tienes un nuevo mensaje en el chat de la orden.",
            orden_id=orden.id,
        )

    db.commit()
    db.refresh(mensaje)
    return mensaje


def obtener_mensaje(db: Session, mensaje_id, chat_id) -> Mensaje | None:
    return (
        db.execute(
            select(Mensaje).where(Mensaje.id == mensaje_id, Mensaje.chat_id == chat_id)
        )
        .scalars()
        .first()
    )


def marcar_mensaje_leido(db: Session, mensaje: Mensaje, usuario: Usuario, orden: OrdenServicio) -> Mensaje:
    if not validar_acceso_chat(db, orden, usuario):
        raise PermissionError("No tienes permisos para leer mensajes de este chat")

    if not mensaje.leido:
        mensaje.leido = True
        db.commit()
        db.refresh(mensaje)
    return mensaje


def contar_mensajes_no_leidos_chat(db: Session, chat_id, usuario_id) -> int:
    result = db.execute(
        select(Mensaje.id).where(
            Mensaje.chat_id == chat_id,
            Mensaje.remitente_id != usuario_id,
            Mensaje.leido.is_(False),
        )
    )
    return len(result.scalars().all())


def marcar_chat_como_leido(db: Session, chat: Chat, usuario: Usuario, orden: OrdenServicio) -> int:
    if not validar_acceso_chat(db, orden, usuario):
        raise PermissionError("No tienes permisos para leer mensajes de este chat")

    mensajes = db.execute(
        select(Mensaje).where(
            Mensaje.chat_id == chat.id,
            Mensaje.remitente_id != usuario.id,
            Mensaje.leido.is_(False),
        )
    ).scalars().all()

    for mensaje in mensajes:
        mensaje.leido = True

    db.commit()
    return len(mensajes)
