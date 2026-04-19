from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.taller import CategoriaServicio, ServicioTaller, Taller
from app.models.usuario import Usuario


def listar_categorias(db: Session, activo: bool | None = None):
    query = select(CategoriaServicio)
    if activo is not None:
        query = query.where(CategoriaServicio.activo == activo)
    result = db.execute(query.order_by(CategoriaServicio.nombre.asc()))
    return result.scalars().all()


def obtener_categoria(db: Session, categoria_id) -> CategoriaServicio | None:
    return db.execute(select(CategoriaServicio).where(CategoriaServicio.id == categoria_id)).scalars().first()


def actualizar_categoria(
    db: Session,
    categoria: CategoriaServicio,
    data: dict,
) -> CategoriaServicio:
    for key, value in data.items():
        setattr(categoria, key, value)
    db.commit()
    db.refresh(categoria)
    return categoria


def obtener_taller(db: Session, taller_id) -> Taller | None:
    return db.execute(select(Taller).where(Taller.id == taller_id)).scalars().first()


def _validar_permiso_taller_o_admin(usuario: Usuario, taller: Taller) -> None:
    if usuario.rol == UserRole.ADMIN:
        return
    if usuario.rol == UserRole.TALLER and taller.usuario_id == usuario.id:
        return
    raise PermissionError("No tienes permisos para gestionar servicios de este taller")


def crear_servicio_taller(
    db: Session,
    taller: Taller,
    categoria: CategoriaServicio,
    usuario: Usuario,
    data: dict,
) -> ServicioTaller:
    _validar_permiso_taller_o_admin(usuario, taller)

    existente = db.execute(
        select(ServicioTaller).where(
            ServicioTaller.taller_id == taller.id,
            ServicioTaller.categoria_id == categoria.id,
        )
    ).scalars().first()
    if existente:
        raise ValueError("El taller ya tiene un servicio para esa categoría")

    if data.get("precio_base_min") is not None:
        data["precio_base_min"] = Decimal(str(data["precio_base_min"]))
    if data.get("precio_base_max") is not None:
        data["precio_base_max"] = Decimal(str(data["precio_base_max"]))
    if (
        data.get("precio_base_min") is not None
        and data.get("precio_base_max") is not None
        and data["precio_base_min"] > data["precio_base_max"]
    ):
        raise ValueError("precio_base_min no puede ser mayor que precio_base_max")

    servicio = ServicioTaller(
        taller_id=taller.id,
        categoria_id=categoria.id,
        descripcion=data.get("descripcion"),
        precio_base_min=data.get("precio_base_min"),
        precio_base_max=data.get("precio_base_max"),
        tiempo_estimado_min=data.get("tiempo_estimado_min"),
        servicio_movil=data.get("servicio_movil", False),
        activo=True,
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


def listar_servicios_taller(db: Session, taller_id, solo_activos: bool = True):
    query = select(ServicioTaller).where(ServicioTaller.taller_id == taller_id)
    if solo_activos:
        query = query.where(ServicioTaller.activo.is_(True))
    result = db.execute(query.order_by(ServicioTaller.creado_en.desc()))
    return result.scalars().all()


def obtener_servicio_taller(db: Session, servicio_id) -> ServicioTaller | None:
    return db.execute(select(ServicioTaller).where(ServicioTaller.id == servicio_id)).scalars().first()


def actualizar_servicio_taller(
    db: Session,
    servicio: ServicioTaller,
    usuario: Usuario,
    data: dict,
) -> ServicioTaller:
    taller = obtener_taller(db, servicio.taller_id)
    if not taller:
        raise ValueError("No se encontró el taller del servicio")
    _validar_permiso_taller_o_admin(usuario, taller)

    if data.get("precio_base_min") is not None:
        data["precio_base_min"] = Decimal(str(data["precio_base_min"]))
    if data.get("precio_base_max") is not None:
        data["precio_base_max"] = Decimal(str(data["precio_base_max"]))

    precio_min = data.get("precio_base_min", servicio.precio_base_min)
    precio_max = data.get("precio_base_max", servicio.precio_base_max)
    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        raise ValueError("precio_base_min no puede ser mayor que precio_base_max")

    for key, value in data.items():
        setattr(servicio, key, value)

    db.commit()
    db.refresh(servicio)
    return servicio


def desactivar_servicio_taller(
    db: Session,
    servicio: ServicioTaller,
    usuario: Usuario,
) -> ServicioTaller:
    taller = obtener_taller(db, servicio.taller_id)
    if not taller:
        raise ValueError("No se encontró el taller del servicio")
    _validar_permiso_taller_o_admin(usuario, taller)

    servicio.activo = False
    db.commit()
    db.refresh(servicio)
    return servicio
