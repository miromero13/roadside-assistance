import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.comunicacion import DispositivoPush
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:  # pragma: no cover - optional dependency
    firebase_admin = None
    credentials = None
    messaging = None


def registrar_dispositivo_push(
    db: Session,
    usuario: Usuario,
    plataforma,
    token_push: str,
) -> DispositivoPush:
    logger.info("Registrando dispositivo push usuario=%s plataforma=%s", usuario.id, plataforma)
    dispositivo = db.execute(
        select(DispositivoPush).where(
            DispositivoPush.usuario_id == usuario.id,
            DispositivoPush.token_push == token_push,
        )
    ).scalars().first()

    if dispositivo:
        dispositivo.plataforma = plataforma
        dispositivo.activo = True
        dispositivo.ultimo_uso_en = datetime.utcnow()
        logger.info("Dispositivo push existente reactivado id=%s token=%s", dispositivo.id, token_push[:12])
    else:
        dispositivo = DispositivoPush(
            usuario_id=usuario.id,
            plataforma=plataforma,
            token_push=token_push,
            activo=True,
            ultimo_uso_en=datetime.utcnow(),
        )
        db.add(dispositivo)
        logger.info("Dispositivo push nuevo creado token=%s", token_push[:12])

    db.commit()
    db.refresh(dispositivo)
    return dispositivo


def listar_dispositivos_usuario(db: Session, usuario_id):
    return (
        db.execute(
            select(DispositivoPush)
            .where(DispositivoPush.usuario_id == usuario_id)
            .order_by(DispositivoPush.registrado_en.desc())
        )
        .scalars()
        .all()
    )


def obtener_dispositivo_usuario(db: Session, dispositivo_id, usuario_id) -> DispositivoPush | None:
    return (
        db.execute(
            select(DispositivoPush).where(
                DispositivoPush.id == dispositivo_id,
                DispositivoPush.usuario_id == usuario_id,
            )
        )
        .scalars()
        .first()
    )


def desactivar_dispositivo_push(db: Session, dispositivo: DispositivoPush) -> DispositivoPush:
    if dispositivo.activo:
        dispositivo.activo = False
        dispositivo.ultimo_uso_en = datetime.utcnow()
        db.commit()
        db.refresh(dispositivo)
    return dispositivo


def _obtener_dispositivos_activos_usuario(db: Session, usuario_id):
    return (
        db.execute(
            select(DispositivoPush).where(
                DispositivoPush.usuario_id == usuario_id,
                DispositivoPush.activo.is_(True),
            )
        )
        .scalars()
        .all()
    )


def _obtener_app_firebase():
    if firebase_admin is None or credentials is None or messaging is None:
        return None

    if firebase_admin._apps:  # type: ignore[attr-defined]
        return firebase_admin.get_app()

    path = settings.firebase_service_account_path
    if not path:
        logger.warning("FIREBASE_SERVICE_ACCOUNT_PATH no está configurado")
        return None

    cred_path = Path(path)
    if not cred_path.is_absolute():
        cred_path = Path(__file__).resolve().parents[2] / cred_path

    logger.info("Buscando credenciales Firebase en %s", cred_path)
    if not cred_path.exists():
        logger.warning("Firebase service account no encontrado: %s", cred_path)
        return None

    logger.info("Inicializando Firebase Admin con %s", cred_path)
    return firebase_admin.initialize_app(credentials.Certificate(str(cred_path)))


def enviar_push_a_usuario(
    db: Session,
    usuario_id,
    titulo: str,
    mensaje: str,
    data: dict[str, str] | None = None,
) -> None:
    dispositivos = _obtener_dispositivos_activos_usuario(db, usuario_id)
    logger.info(
        "Preparando push usuario=%s dispositivos_activos=%s titulo=%s",
        usuario_id,
        len(dispositivos),
        titulo,
    )
    if not dispositivos:
        logger.info("Push omitido usuario=%s sin dispositivos activos", usuario_id)
        return

    app = _obtener_app_firebase()
    if app is None:
        logger.warning("Push omitido usuario=%s porque Firebase no está disponible", usuario_id)
        return

    payload_data = {str(key): str(value) for key, value in (data or {}).items()}
    tokens = [dispositivo.token_push for dispositivo in dispositivos if dispositivo.token_push]
    if not tokens:
        logger.warning("Push omitido usuario=%s sin tokens válidos", usuario_id)
        return

    for token in tokens:
        try:
            logger.info("Enviando push usuario=%s token=%s", usuario_id, token[:12])
            message = messaging.Message(  # type: ignore[union-attr]
                token=token,
                notification=messaging.Notification(title=titulo, body=mensaje),  # type: ignore[union-attr]
                data=payload_data or None,
            )
            message_id = messaging.send(message, app=app)  # type: ignore[union-attr]
            logger.info("Push enviado usuario=%s message_id=%s", usuario_id, message_id)
        except Exception:
            logger.exception("No se pudo enviar push a usuario %s", usuario_id)
            continue


def enviar_push_a_usuarios(
    db: Session,
    usuario_ids,
    titulo: str,
    mensaje: str,
    data: dict[str, str] | None = None,
) -> None:
    for usuario_id in set(usuario_ids):
        enviar_push_a_usuario(db, usuario_id, titulo, mensaje, data=data)
