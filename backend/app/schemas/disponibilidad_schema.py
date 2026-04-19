from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import DiaSemana, PlataformaPush


class HorarioTallerCrearRequest(BaseModel):
    dia_semana: DiaSemana
    hora_apertura: time
    hora_cierre: time
    disponible: bool = True


class HorarioTallerRead(BaseModel):
    id: UUID
    taller_id: UUID
    dia_semana: DiaSemana
    hora_apertura: time
    hora_cierre: time
    disponible: bool

    model_config = {"from_attributes": True}


class HorarioTallerActualizarRequest(BaseModel):
    hora_apertura: time | None = None
    hora_cierre: time | None = None
    disponible: bool | None = None


class BloqueoTallerCrearRequest(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: str | None = None


class BloqueoTallerRead(BaseModel):
    id: UUID
    taller_id: UUID
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: str | None

    model_config = {"from_attributes": True}


class DispositivoPushRegistrarRequest(BaseModel):
    plataforma: PlataformaPush
    token_push: str = Field(min_length=10)


class DispositivoPushRead(BaseModel):
    id: UUID
    usuario_id: UUID
    plataforma: PlataformaPush
    token_push: str
    activo: bool
    registrado_en: datetime
    ultimo_uso_en: datetime | None

    model_config = {"from_attributes": True}
