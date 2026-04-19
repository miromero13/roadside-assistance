from __future__ import annotations

import uuid
from datetime import datetime, time
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import DiaSemana


class Taller(Base):
    __tablename__ = "talleres"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, unique=True
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    direccion: Mapped[str] = mapped_column(String(500), nullable=False)
    latitud: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitud: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    radio_cobertura_km: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, server_default="5.0"
    )
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    foto_url: Mapped[Optional[str]] = mapped_column(String(500))
    acepta_domicilio: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    calificacion_promedio: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, server_default="0.00"
    )
    tiempo_respuesta_promedio_min: Mapped[Optional[int]] = mapped_column(Integer)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="taller")
    horarios: Mapped[List["HorarioTaller"]] = relationship(
        back_populates="taller", cascade="all, delete-orphan"
    )
    bloqueos: Mapped[List["BloqueoTaller"]] = relationship(
        back_populates="taller", cascade="all, delete-orphan"
    )
    servicios: Mapped[List["ServicioTaller"]] = relationship(
        back_populates="taller", cascade="all, delete-orphan"
    )
    mecanicos: Mapped[List["Mecanico"]] = relationship(
        back_populates="taller", cascade="all, delete-orphan"
    )
    ordenes_servicio: Mapped[List["OrdenServicio"]] = relationship(
        back_populates="taller"
    )


class HorarioTaller(Base):
    __tablename__ = "horarios_taller"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    taller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talleres.id"), nullable=False, index=True
    )
    dia_semana: Mapped[DiaSemana] = mapped_column(
        SAEnum(
            DiaSemana,
            name="dia_semana",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    hora_apertura: Mapped[time] = mapped_column(Time, nullable=False)
    hora_cierre: Mapped[time] = mapped_column(Time, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    taller: Mapped["Taller"] = relationship(back_populates="horarios")


class BloqueoTaller(Base):
    __tablename__ = "bloqueos_taller"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    taller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talleres.id"), nullable=False, index=True
    )
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    motivo: Mapped[Optional[str]] = mapped_column(String(300))

    taller: Mapped["Taller"] = relationship(back_populates="bloqueos")


class CategoriaServicio(Base):
    __tablename__ = "categorias_servicio"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    servicios_taller: Mapped[List["ServicioTaller"]] = relationship(
        back_populates="categoria"
    )
    diagnosticos_ia: Mapped[List["DiagnosticoIA"]] = relationship(
        back_populates="categoria"
    )
    ordenes_servicio: Mapped[List["OrdenServicio"]] = relationship(
        back_populates="categoria"
    )


class ServicioTaller(Base):
    __tablename__ = "servicios_taller"
    __table_args__ = (
        UniqueConstraint("taller_id", "categoria_id", name="uq_servicio_taller_categoria"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    taller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talleres.id"), nullable=False, index=True
    )
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categorias_servicio.id"), nullable=False, index=True
    )
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    precio_base_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    precio_base_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tiempo_estimado_min: Mapped[Optional[int]] = mapped_column(Integer)
    servicio_movil: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    taller: Mapped["Taller"] = relationship(back_populates="servicios")
    categoria: Mapped["CategoriaServicio"] = relationship(back_populates="servicios_taller")


class Mecanico(Base):
    __tablename__ = "mecanicos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, unique=True
    )
    taller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talleres.id"), nullable=False, index=True
    )
    especialidad: Mapped[Optional[str]] = mapped_column(String(150))
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    latitud_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    longitud_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    ultima_ubicacion_en: Mapped[Optional[datetime]] = mapped_column(DateTime)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="mecanico")
    taller: Mapped["Taller"] = relationship(back_populates="mecanicos")
    asignaciones: Mapped[List["AsignacionOrden"]] = relationship(
        back_populates="mecanico"
    )
