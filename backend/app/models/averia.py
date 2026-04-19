from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ClasificacionIA, EstadoAveria, MedioTipo, Prioridad


class Averia(Base):
    __tablename__ = "averias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehiculos.id"), nullable=False, index=True
    )
    descripcion_conductor: Mapped[str] = mapped_column(Text, nullable=False)
    latitud_averia: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitud_averia: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    direccion_averia: Mapped[Optional[str]] = mapped_column(String(500))
    prioridad: Mapped[Prioridad] = mapped_column(
        SAEnum(
            Prioridad,
            name="prioridad",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=Prioridad.MEDIA.value,
    )
    estado: Mapped[EstadoAveria] = mapped_column(
        SAEnum(
            EstadoAveria,
            name="estado_averia",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=EstadoAveria.REGISTRADA.value,
    )
    requiere_mas_informacion: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    cancelado_en: Mapped[Optional[datetime]] = mapped_column(DateTime)

    usuario: Mapped["Usuario"] = relationship(back_populates="averias_reportadas")
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="averias")
    medios: Mapped[List["MedioAveria"]] = relationship(
        back_populates="averia", cascade="all, delete-orphan"
    )
    diagnostico_ia: Mapped[Optional["DiagnosticoIA"]] = relationship(
        back_populates="averia", uselist=False, cascade="all, delete-orphan"
    )
    ordenes_servicio: Mapped[List["OrdenServicio"]] = relationship(
        back_populates="averia"
    )


class MedioAveria(Base):
    __tablename__ = "medios_averia"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    averia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("averias.id"), nullable=False, index=True
    )
    tipo: Mapped[MedioTipo] = mapped_column(
        SAEnum(
            MedioTipo,
            name="medio_tipo",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    orden_visualizacion: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="1"
    )
    subido_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    averia: Mapped["Averia"] = relationship(back_populates="medios")


class DiagnosticoIA(Base):
    __tablename__ = "diagnosticos_ia"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    averia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("averias.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categorias_servicio.id"), index=True
    )
    clasificacion: Mapped[ClasificacionIA] = mapped_column(
        SAEnum(
            ClasificacionIA,
            name="clasificacion_ia",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    urgencia: Mapped[Prioridad] = mapped_column(
        SAEnum(
            Prioridad,
            name="urgencia_ia",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    nivel_confianza: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    transcripcion_audio: Mapped[Optional[str]] = mapped_column(Text)
    analisis: Mapped[str] = mapped_column(Text, nullable=False)
    resumen_automatico: Mapped[Optional[str]] = mapped_column(Text)
    recomendacion: Mapped[Optional[str]] = mapped_column(Text)
    danos_visibles: Mapped[Optional[str]] = mapped_column(Text)
    costo_estimado_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    costo_estimado_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    requiere_revision_manual: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    historial_conversacion: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    averia: Mapped["Averia"] = relationship(back_populates="diagnostico_ia")
    categoria: Mapped[Optional["CategoriaServicio"]] = relationship(
        back_populates="diagnosticos_ia"
    )
