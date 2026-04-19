from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import EstadoAveria, MedioTipo, Prioridad


class AveriaCrear(BaseModel):
    vehiculo_id: UUID
    descripcion_conductor: str = Field(min_length=1)
    latitud_averia: float = Field(ge=-90, le=90)
    longitud_averia: float = Field(ge=-180, le=180)
    direccion_averia: str | None = None
    prioridad: Prioridad = Prioridad.MEDIA


class MedioAveriaCrear(BaseModel):
    tipo: MedioTipo
    url: str = Field(min_length=1)
    orden_visualizacion: int = Field(default=1, ge=1, le=20)


class MedioAveriaRead(BaseModel):
    id: UUID
    averia_id: UUID
    tipo: MedioTipo
    url: str
    orden_visualizacion: int
    subido_en: datetime

    model_config = {"from_attributes": True}


class AveriaRead(BaseModel):
    id: UUID
    usuario_id: UUID
    vehiculo_id: UUID
    descripcion_conductor: str
    latitud_averia: float
    longitud_averia: float
    direccion_averia: str | None
    prioridad: Prioridad
    estado: EstadoAveria
    requiere_mas_informacion: bool
    creado_en: datetime
    actualizado_en: datetime
    cancelado_en: datetime | None

    model_config = {"from_attributes": True}


class AveriaDetalleRead(AveriaRead):
    medios: list[MedioAveriaRead]
