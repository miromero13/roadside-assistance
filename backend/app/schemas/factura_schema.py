from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class FacturaRead(BaseModel):
    id: UUID
    pago_id: UUID
    orden_id: UUID
    numero_factura: str
    datos_emisor: dict
    datos_receptor: dict
    items: dict
    subtotal: Decimal
    impuesto: Decimal
    total: Decimal
    pdf_url: str | None
    emitida_en: datetime

    model_config = {"from_attributes": True}
