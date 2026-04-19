from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import TipoNotificacion


class NotificacionRead(BaseModel):
    id: UUID
    usuario_id: UUID
    orden_id: UUID | None
    titulo: str
    mensaje: str
    tipo: TipoNotificacion
    leida: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


class NotificacionesResponse(BaseModel):
    data: list[NotificacionRead]
    countData: int
