from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PlataformaPush, TipoCalificador, TipoMensaje, TipoNotificacion


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, unique=True, index=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    orden: Mapped["OrdenServicio"] = relationship(back_populates="chat")
    mensajes: Mapped[List["Mensaje"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )


class Mensaje(Base):
    __tablename__ = "mensajes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False, index=True
    )
    remitente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    contenido: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[TipoMensaje] = mapped_column(
        SAEnum(
            TipoMensaje,
            name="tipo_mensaje",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=TipoMensaje.TEXTO.value,
    )
    media_url: Mapped[Optional[str]] = mapped_column(String(500))
    leido: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    enviado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    chat: Mapped["Chat"] = relationship(back_populates="mensajes")
    remitente: Mapped["Usuario"] = relationship(back_populates="mensajes_enviados")


class Calificacion(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (
        UniqueConstraint("orden_id", "calificador_id", name="uq_calificacion_orden_calificador"),
        CheckConstraint("puntuacion BETWEEN 1 AND 5", name="ck_calificacion_puntuacion"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), nullable=False, index=True
    )
    calificador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    calificado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    tipo_calificador: Mapped[TipoCalificador] = mapped_column(
        SAEnum(
            TipoCalificador,
            name="tipo_calificador",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    puntuacion: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    orden: Mapped["OrdenServicio"] = relationship(back_populates="calificaciones")
    calificador: Mapped["Usuario"] = relationship(
        back_populates="calificaciones_dadas",
        foreign_keys=[calificador_id],
    )
    calificado: Mapped["Usuario"] = relationship(
        back_populates="calificaciones_recibidas",
        foreign_keys=[calificado_id],
    )


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    orden_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes_servicio.id"), index=True
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[TipoNotificacion] = mapped_column(
        SAEnum(
            TipoNotificacion,
            name="tipo_notificacion",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    leida: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="notificaciones")
    orden: Mapped[Optional["OrdenServicio"]] = relationship(back_populates="notificaciones")


class DispositivoPush(Base):
    __tablename__ = "dispositivos_push"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    plataforma: Mapped[PlataformaPush] = mapped_column(
        SAEnum(
            PlataformaPush,
            name="plataforma_push",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    token_push: Mapped[str] = mapped_column(String(500), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    registrado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    ultimo_uso_en: Mapped[Optional[datetime]] = mapped_column(DateTime)

    usuario: Mapped["Usuario"] = relationship(back_populates="dispositivos_push")
