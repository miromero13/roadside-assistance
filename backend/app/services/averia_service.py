from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.averia import Averia, MedioAveria
from app.models.enums import EstadoAveria
from app.models.usuario import Vehiculo
from app.schemas.averia_schema import AveriaCrear, MedioAveriaCrear


def crear_averia(db: Session, payload: AveriaCrear, usuario_id) -> Averia:
    vehiculo = db.execute(
        select(Vehiculo).where(Vehiculo.id == payload.vehiculo_id)
    ).scalars().first()
    if not vehiculo:
        raise ValueError("El vehículo no existe")
    if vehiculo.usuario_id != usuario_id:
        raise PermissionError("No puedes registrar averías sobre un vehículo que no te pertenece")

    averia = Averia(
        usuario_id=usuario_id,
        vehiculo_id=payload.vehiculo_id,
        descripcion_conductor=payload.descripcion_conductor,
        latitud_averia=Decimal(str(payload.latitud_averia)),
        longitud_averia=Decimal(str(payload.longitud_averia)),
        direccion_averia=payload.direccion_averia,
        prioridad=payload.prioridad,
        estado=EstadoAveria.REGISTRADA,
    )
    db.add(averia)
    db.commit()
    db.refresh(averia)
    return averia


def listar_averias_por_usuario(db: Session, usuario_id):
    result = db.execute(
        select(Averia)
        .where(Averia.usuario_id == usuario_id)
        .options(selectinload(Averia.medios))
        .order_by(Averia.creado_en.desc())
    )
    return result.scalars().all()


def listar_averias(db: Session):
    result = db.execute(
        select(Averia).options(selectinload(Averia.medios)).order_by(Averia.creado_en.desc())
    )
    return result.scalars().all()


def obtener_averia(db: Session, averia_id):
    result = db.execute(
        select(Averia)
        .where(Averia.id == averia_id)
        .options(selectinload(Averia.medios))
    )
    return result.scalars().first()


def agregar_medio_averia(
    db: Session,
    averia: Averia,
    payload: MedioAveriaCrear,
) -> MedioAveria:
    medio = MedioAveria(
        averia_id=averia.id,
        tipo=payload.tipo,
        url=payload.url,
        orden_visualizacion=payload.orden_visualizacion,
    )
    db.add(medio)
    db.commit()
    db.refresh(medio)
    return medio
