import math
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.averia import Averia
from app.models.taller import ServicioTaller, Taller


def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radio_tierra_km = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radio_tierra_km * c


def obtener_averia_de_conductor(db: Session, averia_id: UUID, usuario_id: UUID) -> Averia | None:
    result = db.execute(
        select(Averia).where(Averia.id == averia_id, Averia.usuario_id == usuario_id)
    )
    return result.scalars().first()


def listar_talleres_candidatos(
    db: Session,
    latitud: float,
    longitud: float,
    categoria_id: UUID | None = None,
):
    base_query = select(Taller).where(Taller.activo.is_(True))

    if categoria_id is not None:
        base_query = (
            select(Taller)
            .join(ServicioTaller, ServicioTaller.taller_id == Taller.id)
            .where(
                Taller.activo.is_(True),
                ServicioTaller.categoria_id == categoria_id,
                ServicioTaller.activo.is_(True),
            )
        )

    talleres = db.execute(base_query).scalars().all()

    candidatos = []
    for taller in talleres:
        distancia = calcular_distancia_km(
            latitud,
            longitud,
            float(taller.latitud),
            float(taller.longitud),
        )

        if distancia <= float(Decimal(taller.radio_cobertura_km)):
            candidatos.append(
                {
                    "id": taller.id,
                    "nombre": taller.nombre,
                    "direccion": taller.direccion,
                    "telefono": taller.telefono,
                    "latitud": float(taller.latitud),
                    "longitud": float(taller.longitud),
                    "radio_cobertura_km": float(taller.radio_cobertura_km),
                    "calificacion_promedio": float(taller.calificacion_promedio),
                    "tiempo_respuesta_promedio_min": taller.tiempo_respuesta_promedio_min,
                    "acepta_domicilio": taller.acepta_domicilio,
                    "distancia_km": round(distancia, 2),
                }
            )

    return sorted(candidatos, key=lambda item: item["distancia_km"])
