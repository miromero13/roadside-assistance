from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoAsignacion, EstadoOrdenServicio


class OrdenServicio(Base):
    __tablename__ = "ordenes_servicio"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    averia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("averias.id"), nullable=False, index=True
    )
    taller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talleres.id"), nullable=False, index=True
    )
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categorias_servicio.id"), nullable=False, index=True
    )
    estado: Mapped[EstadoOrdenServicio] = mapped_column(
        SAEnum(
            EstadoOrdenServicio,
            name="estado_orden_servicio",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=EstadoOrdenServicio.PENDIENTE_RESPUESTA.value,
    )
    es_domicilio: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    notas_conductor: Mapped[Optional[str]] = mapped_column(Text)
    notas_taller: Mapped[Optional[str]] = mapped_column(Text)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text)
    motivo_cancelacion: Mapped[Optional[str]] = mapped_column(Text)
    vence_respuesta_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    tiempo_estimado_respuesta_min: Mapped[Optional[int]] = mapped_column(Integer)
    tiempo_estimado_llegada_min: Mapped[Optional[int]] = mapped_column(Integer)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    respondido_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    aceptado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rechazado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    iniciado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)

    averia: Mapped["Averia"] = relationship(back_populates="ordenes_servicio")
    taller: Mapped["Taller"] = relationship(back_populates="ordenes_servicio")
    categoria: Mapped["CategoriaServicio"] = relationship(
        back_populates="ordenes_servicio"
    )
    asignaciones: Mapped[List["AsignacionOrden"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    presupuestos: Mapped[List["Presupuesto"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    pagos: Mapped[List["Pago"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    comisiones: Mapped[List["ComisionPlataforma"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    chat: Mapped[Optional["Chat"]] = relationship(
        back_populates="orden", uselist=False, cascade="all, delete-orphan"
    )
    calificaciones: Mapped[List["Calificacion"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    notificaciones: Mapped[List["Notificacion"]] = relationship(
        back_populates="orden"
    )
    historial_estados: Mapped[List["HistorialEstadoOrden"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    metrica_servicio: Mapped[Optional["MetricaServicio"]] = relationship(
        back_populates="orden", uselist=False, cascade="all, delete-orphan"
    )


class AsignacionOrden(Base):
    __tablename__ = "asignaciones_orden"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    mecanico_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mecanicos.id"), nullable=False, index=True
    )
    asignado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    estado: Mapped[EstadoAsignacion] = mapped_column(
        SAEnum(
            EstadoAsignacion,
            name="estado_asignacion",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=EstadoAsignacion.ASIGNADO.value,
    )
    notas: Mapped[Optional[str]] = mapped_column(Text)
    asignado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    salida_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    llegada_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    finalizado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)

    orden: Mapped["OrdenServicio"] = relationship(back_populates="asignaciones")
    mecanico: Mapped["Mecanico"] = relationship(back_populates="asignaciones")
    asignado_por_usuario: Mapped["Usuario"] = relationship(
        back_populates="asignaciones_realizadas",
        foreign_keys=[asignado_por],
    )


class HistorialEstadoOrden(Base):
    __tablename__ = "historial_estados_orden"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    estado_anterior: Mapped[Optional[str]] = mapped_column(String(50))
    estado_nuevo: Mapped[str] = mapped_column(String(50), nullable=False)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), index=True
    )
    observacion: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    orden: Mapped["OrdenServicio"] = relationship(back_populates="historial_estados")
    usuario: Mapped[Optional["Usuario"]] = relationship(back_populates="cambios_estado_orden")


class MetricaServicio(Base):
    __tablename__ = "metricas_servicio"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ordenes_servicio.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    tiempo_respuesta_min: Mapped[Optional[int]] = mapped_column(Integer)
    tiempo_llegada_min: Mapped[Optional[int]] = mapped_column(Integer)
    tiempo_resolucion_min: Mapped[Optional[int]] = mapped_column(Integer)
    calificacion_final: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    orden: Mapped["OrdenServicio"] = relationship(back_populates="metrica_servicio")
