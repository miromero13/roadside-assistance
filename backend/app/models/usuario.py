from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TipoCombustible, UserRole


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    foto_url: Mapped[Optional[str]] = mapped_column(String(500))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    vehiculos: Mapped[List["Vehiculo"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    taller: Mapped[Optional["Taller"]] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    mecanico: Mapped[Optional["Mecanico"]] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    averias_reportadas: Mapped[List["Averia"]] = relationship(back_populates="usuario")
    mensajes_enviados: Mapped[List["Mensaje"]] = relationship(back_populates="remitente")
    calificaciones_dadas: Mapped[List["Calificacion"]] = relationship(
        back_populates="calificador",
        foreign_keys="Calificacion.calificador_id",
    )
    calificaciones_recibidas: Mapped[List["Calificacion"]] = relationship(
        back_populates="calificado",
        foreign_keys="Calificacion.calificado_id",
    )
    notificaciones: Mapped[List["Notificacion"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    dispositivos_push: Mapped[List["DispositivoPush"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    asignaciones_realizadas: Mapped[List["AsignacionOrden"]] = relationship(
        back_populates="asignado_por_usuario",
        foreign_keys="AsignacionOrden.asignado_por",
    )
    cambios_estado_orden: Mapped[List["HistorialEstadoOrden"]] = relationship(
        back_populates="usuario"
    )


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    placa: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    color: Mapped[Optional[str]] = mapped_column(String(50))
    tipo_combustible: Mapped[TipoCombustible] = mapped_column(
        SAEnum(
            TipoCombustible,
            name="tipo_combustible",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    foto_url: Mapped[Optional[str]] = mapped_column(String(500))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="vehiculos")
    averias: Mapped[List["Averia"]] = relationship(back_populates="vehiculo")
