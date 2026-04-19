from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import EstadoComision


class ComisionRead(BaseModel):
    id: UUID
    orden_id: UUID
    pago_id: UUID
    monto_base: Decimal
    porcentaje: Decimal
    monto_comision: Decimal
    estado: EstadoComision
    creado_en: datetime
    pagado_en: datetime | None

    model_config = {"from_attributes": True}
