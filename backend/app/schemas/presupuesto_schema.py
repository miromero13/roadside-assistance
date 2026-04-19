from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import EstadoPresupuesto


class PresupuestoCrearRequest(BaseModel):
    descripcion_trabajos: str = Field(min_length=3)
    items_detalle: dict
    monto_repuestos: Decimal = Field(ge=0)
    monto_mano_obra: Decimal = Field(ge=0)


class PresupuestoRead(BaseModel):
    id: UUID
    orden_id: UUID
    version: int
    descripcion_trabajos: str
    items_detalle: dict
    monto_repuestos: Decimal
    monto_mano_obra: Decimal
    monto_total: Decimal
    estado: EstadoPresupuesto
    motivo_rechazo: str | None
    enviado_en: datetime
    respondido_en: datetime | None

    model_config = {"from_attributes": True}


class PresupuestoAprobarRequest(BaseModel):
    observacion: str | None = None


class PresupuestoRechazarRequest(BaseModel):
    motivo_rechazo: str = Field(min_length=3)
