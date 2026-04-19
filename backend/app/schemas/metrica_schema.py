from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MetricaServicioRead(BaseModel):
    id: UUID
    orden_id: UUID
    tiempo_respuesta_min: int | None
    tiempo_llegada_min: int | None
    tiempo_resolucion_min: int | None
    calificacion_final: Decimal | None
    creado_en: datetime

    model_config = {"from_attributes": True}
