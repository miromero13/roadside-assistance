from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import EstadoPago, MetodoPago


class PagoCrearRequest(BaseModel):
    orden_id: UUID
    presupuesto_id: UUID
    metodo: MetodoPago
    monto: Decimal = Field(gt=0)


class PagoConfirmarRequest(BaseModel):
    referencia_externa: str | None = None


class PagoRead(BaseModel):
    id: UUID
    orden_id: UUID
    presupuesto_id: UUID | None
    monto: Decimal
    metodo: MetodoPago
    estado: EstadoPago
    referencia_externa: str | None
    pagado_en: datetime | None
    creado_en: datetime

    model_config = {"from_attributes": True}
