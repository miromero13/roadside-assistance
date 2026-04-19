import uuid
from dataclasses import dataclass
from decimal import Decimal

from app.models.enums import MetodoPago


@dataclass
class IntencionPago:
    referencia_externa: str
    estado: str


class PaymentGateway:
    def crear_intencion_pago(self, monto: Decimal, metodo: MetodoPago) -> IntencionPago:
        raise NotImplementedError

    def confirmar_pago(self, referencia_externa: str) -> bool:
        raise NotImplementedError


class DummyPaymentGateway(PaymentGateway):
    def crear_intencion_pago(self, monto: Decimal, metodo: MetodoPago) -> IntencionPago:
        _ = (monto, metodo)
        return IntencionPago(
            referencia_externa=f"pay_{uuid.uuid4().hex}",
            estado="pendiente",
        )

    def confirmar_pago(self, referencia_externa: str) -> bool:
        _ = referencia_externa
        return True
