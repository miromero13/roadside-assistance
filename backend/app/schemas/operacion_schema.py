from uuid import UUID

from pydantic import BaseModel, Field


class MecanicoDisponibilidadRequest(BaseModel):
    disponible: bool


class TallerRead(BaseModel):
    id: UUID
    usuario_id: UUID
    nombre: str
    descripcion: str | None
    direccion: str
    latitud: float
    longitud: float
    radio_cobertura_km: float
    telefono: str
    foto_url: str | None
    acepta_domicilio: bool
    calificacion_promedio: float
    tiempo_respuesta_promedio_min: int | None
    activo: bool

    model_config = {"from_attributes": True}


class TallerActualizarRequest(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    direccion: str | None = None
    latitud: float | None = Field(default=None, ge=-90, le=90)
    longitud: float | None = Field(default=None, ge=-180, le=180)
    radio_cobertura_km: float | None = Field(default=None, gt=0)
    telefono: str | None = None
    foto_url: str | None = None
    acepta_domicilio: bool | None = None
