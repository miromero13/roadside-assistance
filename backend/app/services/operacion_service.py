from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.enums import UserRole
from app.models.taller import Mecanico, Taller
from app.models.usuario import Usuario


def obtener_mecanico(db: Session, mecanico_id) -> Mecanico | None:
    return db.execute(select(Mecanico).where(Mecanico.id == mecanico_id)).scalars().first()


def listar_mecanicos_para_usuario(
    db: Session,
    usuario_actual: Usuario,
    disponible: bool | None = None,
) -> list[Mecanico]:
    query = select(Mecanico).options(selectinload(Mecanico.usuario))

    if usuario_actual.rol == UserRole.ADMIN:
        pass
    elif usuario_actual.rol == UserRole.TALLER:
        taller = db.execute(select(Taller).where(Taller.usuario_id == usuario_actual.id)).scalars().first()
        if not taller:
            return []
        query = query.where(Mecanico.taller_id == taller.id)
    else:
        raise PermissionError("No tienes permisos para listar mecánicos")

    if disponible is not None:
        query = query.where(Mecanico.disponible == disponible)

    return db.execute(query.order_by(Mecanico.creado_en.desc())).scalars().all()


def listar_mecanicos_por_taller(
    db: Session,
    taller_id,
    disponible: bool | None = None,
) -> list[Mecanico]:
    query = select(Mecanico).options(selectinload(Mecanico.usuario)).where(Mecanico.taller_id == taller_id)

    if disponible is not None:
        query = query.where(Mecanico.disponible == disponible)

    return db.execute(query.order_by(Mecanico.creado_en.desc())).scalars().all()


def obtener_taller(db: Session, taller_id) -> Taller | None:
    return db.execute(select(Taller).where(Taller.id == taller_id)).scalars().first()


def obtener_taller_por_usuario(db: Session, usuario_id) -> Taller | None:
    return db.execute(select(Taller).where(Taller.usuario_id == usuario_id)).scalars().first()


def listar_talleres(db: Session) -> list[Taller]:
    query = select(Taller).options(selectinload(Taller.usuario))
    return db.execute(query.order_by(Taller.creado_en.desc())).scalars().all()


def _es_taller_dueno(db: Session, taller: Taller, usuario_id) -> bool:
    return taller.usuario_id == usuario_id


def actualizar_disponibilidad_mecanico(
    db: Session,
    mecanico: Mecanico,
    disponible: bool,
    usuario_actual: Usuario,
) -> Mecanico:
    if usuario_actual.rol == UserRole.ADMIN:
        pass
    elif usuario_actual.rol == UserRole.TALLER:
        taller = obtener_taller(db, mecanico.taller_id)
        if not taller or not _es_taller_dueno(db, taller, usuario_actual.id):
            raise PermissionError("No puedes modificar mecánicos de otro taller")
    else:
        raise PermissionError("No tienes permisos para actualizar disponibilidad")

    mecanico.disponible = disponible
    db.commit()
    db.refresh(mecanico)
    return mecanico


def actualizar_taller(
    db: Session,
    taller: Taller,
    usuario_actual: Usuario,
    data: dict,
) -> Taller:
    if usuario_actual.rol == UserRole.ADMIN:
        pass
    elif usuario_actual.rol == UserRole.TALLER:
        if not _es_taller_dueno(db, taller, usuario_actual.id):
            raise PermissionError("No puedes actualizar un taller que no te pertenece")
    else:
        raise PermissionError("No tienes permisos para actualizar taller")

    if "latitud" in data and data["latitud"] is not None:
        data["latitud"] = Decimal(str(data["latitud"]))
    if "longitud" in data and data["longitud"] is not None:
        data["longitud"] = Decimal(str(data["longitud"]))
    if "radio_cobertura_km" in data and data["radio_cobertura_km"] is not None:
        data["radio_cobertura_km"] = Decimal(str(data["radio_cobertura_km"]))

    for key, value in data.items():
        setattr(taller, key, value)

    db.commit()
    db.refresh(taller)
    return taller
