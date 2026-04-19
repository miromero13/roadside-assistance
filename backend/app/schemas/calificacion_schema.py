from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import TipoCalificador


class CalificacionCrearRequest(BaseModel):
    puntuacion: int = Field(ge=1, le=5)
    comentario: str | None = None


class CalificacionRead(BaseModel):
    id: UUID
    orden_id: UUID
    calificador_id: UUID
    calificado_id: UUID
    tipo_calificador: TipoCalificador
    puntuacion: int
    comentario: str | None
    creado_en: datetime

    model_config = {"from_attributes": True}
