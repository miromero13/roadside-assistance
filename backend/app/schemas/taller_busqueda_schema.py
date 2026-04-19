from uuid import UUID

from pydantic import BaseModel


class TallerCandidatoRead(BaseModel):
    id: UUID
    nombre: str
    direccion: str
    telefono: str
    latitud: float
    longitud: float
    radio_cobertura_km: float
    calificacion_promedio: float
    tiempo_respuesta_promedio_min: int | None
    acepta_domicilio: bool
    distancia_km: float


class TalleresCandidatosResponse(BaseModel):
    data: list[TallerCandidatoRead]
    countData: int
