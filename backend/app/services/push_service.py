from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comunicacion import DispositivoPush
from app.models.usuario import Usuario


def registrar_dispositivo_push(
    db: Session,
    usuario: Usuario,
    plataforma,
    token_push: str,
) -> DispositivoPush:
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
    else:
        dispositivo = DispositivoPush(
            usuario_id=usuario.id,
            plataforma=plataforma,
            token_push=token_push,
            activo=True,
            ultimo_uso_en=datetime.utcnow(),
        )
        db.add(dispositivo)

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
