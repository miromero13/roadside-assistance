from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, SmallInteger, String, Text, UniqueConstraint, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoComision, EstadoPago, EstadoPresupuesto, MetodoPago


class Presupuesto(Base):
    __tablename__ = "presupuestos"
    __table_args__ = (
        UniqueConstraint("orden_id", "version", name="uq_presupuesto_orden_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="1"
    )
    descripcion_trabajos: Mapped[str] = mapped_column(Text, nullable=False)
    items_detalle: Mapped[dict] = mapped_column(JSONB, nullable=False)
    monto_repuestos: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00"
    )
    monto_mano_obra: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00"
    )
    monto_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[EstadoPresupuesto] = mapped_column(
        SAEnum(
            EstadoPresupuesto,
            name="estado_presupuesto",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=EstadoPresupuesto.ENVIADO.value,
    )
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text)
    enviado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    respondido_en: Mapped[Optional[datetime]] = mapped_column(DateTime)

    orden: Mapped["OrdenServicio"] = relationship(back_populates="presupuestos")
    pagos: Mapped[List["Pago"]] = relationship(back_populates="presupuesto")


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    presupuesto_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("presupuestos.id"), index=True
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    metodo: Mapped[MetodoPago] = mapped_column(
        SAEnum(
            MetodoPago,
            name="metodo_pago",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    estado: Mapped[EstadoPago] = mapped_column(
        SAEnum(
            EstadoPago,
            name="estado_pago",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=EstadoPago.PENDIENTE.value,
    )
    referencia_externa: Mapped[Optional[str]] = mapped_column(String(300))
    pagado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    orden: Mapped["OrdenServicio"] = relationship(back_populates="pagos")
    presupuesto: Mapped[Optional["Presupuesto"]] = relationship(back_populates="pagos")
    factura: Mapped[Optional["Factura"]] = relationship(
        back_populates="pago", uselist=False, cascade="all, delete-orphan"
    )
    comisiones: Mapped[List["ComisionPlataforma"]] = relationship(
        back_populates="pago", cascade="all, delete-orphan"
    )


class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pago_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pagos.id"), nullable=False, unique=True, index=True
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    numero_factura: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    datos_emisor: Mapped[dict] = mapped_column(JSONB, nullable=False)
    datos_receptor: Mapped[dict] = mapped_column(JSONB, nullable=False)
    items: Mapped[dict] = mapped_column(JSONB, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    impuesto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00"
    )
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500))
    emitida_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    pago: Mapped["Pago"] = relationship(back_populates="factura")
    orden: Mapped["OrdenServicio"] = relationship()


class ComisionPlataforma(Base):
    __tablename__ = "comisiones_plataforma"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    pago_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pagos.id"), nullable=False, index=True
    )
    monto_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, server_default="10.00"
    )
    monto_comision: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[EstadoComision] = mapped_column(
        SAEnum(
            EstadoComision,
            name="estado_comision",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=EstadoComision.PENDIENTE.value,
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    pagado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)

    orden: Mapped["OrdenServicio"] = relationship(back_populates="comisiones")
    pago: Mapped["Pago"] = relationship(back_populates="comisiones")
