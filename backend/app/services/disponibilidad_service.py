from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.taller import BloqueoTaller, HorarioTaller, Taller
from app.models.usuario import Usuario


def obtener_taller(db: Session, taller_id) -> Taller | None:
    return db.execute(select(Taller).where(Taller.id == taller_id)).scalars().first()


def _validar_acceso_taller(db: Session, taller: Taller, usuario: Usuario) -> None:
    if usuario.rol == UserRole.ADMIN:
        return
    if usuario.rol == UserRole.TALLER and taller.usuario_id == usuario.id:
        return
    raise PermissionError("No tienes permisos para gestionar disponibilidad de este taller")


def listar_horarios_taller(db: Session, taller_id):
    return (
        db.execute(
            select(HorarioTaller)
            .where(HorarioTaller.taller_id == taller_id)
            .order_by(HorarioTaller.dia_semana.asc(), HorarioTaller.hora_apertura.asc())
        )
        .scalars()
        .all()
    )


def crear_horario_taller(db: Session, taller: Taller, usuario: Usuario, data: dict) -> HorarioTaller:
    _validar_acceso_taller(db, taller, usuario)
    horario = HorarioTaller(taller_id=taller.id, **data)
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario


def obtener_horario(db: Session, horario_id, taller_id) -> HorarioTaller | None:
    return (
        db.execute(
            select(HorarioTaller).where(
                HorarioTaller.id == horario_id,
                HorarioTaller.taller_id == taller_id,
            )
        )
        .scalars()
        .first()
    )


def actualizar_horario_taller(
    db: Session,
    horario: HorarioTaller,
    taller: Taller,
    usuario: Usuario,
    data: dict,
) -> HorarioTaller:
    _validar_acceso_taller(db, taller, usuario)
    for key, value in data.items():
        setattr(horario, key, value)
    db.commit()
    db.refresh(horario)
    return horario


def eliminar_horario_taller(db: Session, horario: HorarioTaller, taller: Taller, usuario: Usuario) -> None:
    _validar_acceso_taller(db, taller, usuario)
    db.delete(horario)
    db.commit()


def listar_bloqueos_taller(db: Session, taller_id):
    return (
        db.execute(
            select(BloqueoTaller)
            .where(BloqueoTaller.taller_id == taller_id)
            .order_by(BloqueoTaller.fecha_inicio.desc())
        )
        .scalars()
        .all()
    )


def crear_bloqueo_taller(db: Session, taller: Taller, usuario: Usuario, data: dict) -> BloqueoTaller:
    _validar_acceso_taller(db, taller, usuario)
    if data["fecha_fin"] <= data["fecha_inicio"]:
        raise ValueError("fecha_fin debe ser mayor a fecha_inicio")
    bloqueo = BloqueoTaller(taller_id=taller.id, **data)
    db.add(bloqueo)
    db.commit()
    db.refresh(bloqueo)
    return bloqueo


def obtener_bloqueo(db: Session, bloqueo_id, taller_id) -> BloqueoTaller | None:
    return (
        db.execute(
            select(BloqueoTaller).where(
                BloqueoTaller.id == bloqueo_id,
                BloqueoTaller.taller_id == taller_id,
            )
        )
        .scalars()
        .first()
    )


def eliminar_bloqueo_taller(db: Session, bloqueo: BloqueoTaller, taller: Taller, usuario: Usuario) -> None:
    _validar_acceso_taller(db, taller, usuario)
    db.delete(bloqueo)
    db.commit()
