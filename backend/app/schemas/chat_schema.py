from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import TipoMensaje


class ChatRead(BaseModel):
    id: UUID
    orden_id: UUID
    creado_en: datetime

    model_config = {"from_attributes": True}


class MensajeCrearRequest(BaseModel):
    contenido: str | None = Field(default=None, min_length=1)
    tipo: TipoMensaje = TipoMensaje.TEXTO
    media_url: str | None = None


class MensajeRead(BaseModel):
    id: UUID
    chat_id: UUID
    remitente_id: UUID
    contenido: str | None
    tipo: TipoMensaje
    media_url: str | None
    leido: bool
    enviado_en: datetime

    model_config = {"from_attributes": True}
