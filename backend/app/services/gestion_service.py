from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.hash import hash_password
from app.models.enums import UserRole
from app.models.taller import CategoriaServicio, Mecanico, Taller
from app.models.usuario import Usuario
from app.schemas.gestion_schema import CategoriaServicioCrear, MecanicoCrearPorTaller, TallerCrearPorAdmin


def crear_taller_por_admin(db: Session, payload: TallerCrearPorAdmin) -> tuple[Usuario, Taller]:
    usuario_taller = Usuario(
        nombre=payload.nombre_admin,
        apellido=payload.apellido_admin,
        email=payload.email_admin,
        telefono=payload.telefono_admin,
        password_hash=hash_password(payload.password_admin),
        rol=UserRole.TALLER,
    )
    db.add(usuario_taller)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ValueError("El correo del administrador de taller ya está registrado")

    taller = Taller(
        usuario_id=usuario_taller.id,
        nombre=payload.nombre_taller,
        descripcion=payload.descripcion,
        direccion=payload.direccion,
        latitud=Decimal(str(payload.latitud)),
        longitud=Decimal(str(payload.longitud)),
        radio_cobertura_km=Decimal(str(payload.radio_cobertura_km)),
        telefono=payload.telefono_taller,
        foto_url=payload.foto_url,
        acepta_domicilio=payload.acepta_domicilio,
    )
    db.add(taller)

    try:
        db.commit()
        db.refresh(usuario_taller)
        db.refresh(taller)
    except IntegrityError:
        db.rollback()
        raise ValueError("No se pudo crear el taller por restricción de datos")

    return usuario_taller, taller


def crear_mecanico_por_taller(
    db: Session,
    payload: MecanicoCrearPorTaller,
    usuario_taller: Usuario,
) -> tuple[Usuario, Mecanico]:
    taller = db.query(Taller).filter(Taller.usuario_id == usuario_taller.id).first()
    if not taller:
        raise ValueError("El usuario actual no tiene un taller asociado")

    usuario_mecanico = Usuario(
        nombre=payload.nombre,
        apellido=payload.apellido,
        email=payload.email,
        telefono=payload.telefono,
        password_hash=hash_password(payload.password),
        rol=UserRole.MECANICO,
    )
    db.add(usuario_mecanico)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ValueError("El correo del mecánico ya está registrado")

    mecanico = Mecanico(
        usuario_id=usuario_mecanico.id,
        taller_id=taller.id,
        especialidad=payload.especialidad,
    )
    db.add(mecanico)

    try:
        db.commit()
        db.refresh(usuario_mecanico)
        db.refresh(mecanico)
    except IntegrityError:
        db.rollback()
        raise ValueError("No se pudo crear el mecánico por restricción de datos")

    return usuario_mecanico, mecanico


def crear_categoria_servicio(db: Session, payload: CategoriaServicioCrear) -> CategoriaServicio:
    categoria = CategoriaServicio(
        nombre=payload.nombre.strip(),
        descripcion=payload.descripcion,
    )
    db.add(categoria)
    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError:
        db.rollback()
        raise ValueError("Ya existe una categoría con ese nombre")
    return categoria
