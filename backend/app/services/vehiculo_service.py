from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.usuario import Vehiculo
from app.schemas.vehiculo_schema import VehiculoActualizar, VehiculoCrear


def crear_vehiculo(db: Session, payload: VehiculoCrear, usuario_id) -> Vehiculo:
    vehiculo = Vehiculo(
        usuario_id=usuario_id,
        marca=payload.marca,
        modelo=payload.modelo,
        anio=payload.anio,
        placa=payload.placa,
        color=payload.color,
        tipo_combustible=payload.tipo_combustible,
        foto_url=payload.foto_url,
    )
    db.add(vehiculo)
    try:
        db.commit()
        db.refresh(vehiculo)
    except IntegrityError:
        db.rollback()
        raise ValueError("No se pudo crear el vehículo. Verifica placa única y datos válidos")
    return vehiculo


def listar_vehiculos_por_usuario(db: Session, usuario_id):
    result = db.execute(
        select(Vehiculo).where(Vehiculo.usuario_id == usuario_id).order_by(Vehiculo.creado_en.desc())
    )
    return result.scalars().all()


def obtener_vehiculo_por_id(db: Session, vehiculo_id):
    result = db.execute(select(Vehiculo).where(Vehiculo.id == vehiculo_id))
    return result.scalars().first()


def actualizar_vehiculo(db: Session, vehiculo: Vehiculo, payload: VehiculoActualizar) -> Vehiculo:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(vehiculo, key, value)
    try:
        db.commit()
        db.refresh(vehiculo)
    except IntegrityError:
        db.rollback()
        raise ValueError("No se pudo actualizar el vehículo. Verifica placa única y datos válidos")
    return vehiculo


def eliminar_vehiculo(db: Session, vehiculo: Vehiculo) -> None:
    tiene_averias = db.execute(
        select(Averia.id).where(Averia.vehiculo_id == vehiculo.id).limit(1)
    ).scalar_one_or_none()
    if tiene_averias:
        raise ValueError("No se puede eliminar un vehículo con averías registradas")

    db.delete(vehiculo)
    db.commit()
