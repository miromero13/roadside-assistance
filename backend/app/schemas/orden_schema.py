from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import EstadoAsignacion, EstadoOrdenServicio


class OrdenCrearPorSeleccionManual(BaseModel):
    averia_id: UUID
    taller_id: UUID
    categoria_id: UUID
    es_domicilio: bool = False
    notas_conductor: str | None = None


class OrdenRead(BaseModel):
    id: UUID
    averia_id: UUID
    taller_id: UUID
    categoria_id: UUID
    estado: EstadoOrdenServicio
    es_domicilio: bool
    notas_conductor: str | None
    notas_taller: str | None
    motivo_rechazo: str | None
    motivo_cancelacion: str | None
    tiempo_estimado_respuesta_min: int | None
    tiempo_estimado_llegada_min: int | None
    creado_en: datetime
    respondido_en: datetime | None
    aceptado_en: datetime | None
    rechazado_en: datetime | None
    iniciado_en: datetime | None
    completado_en: datetime | None
    cancelado_en: datetime | None

    model_config = {"from_attributes": True}


class OrdenesResponse(BaseModel):
    data: list[OrdenRead]
    countData: int


class OrdenAceptarRequest(BaseModel):
    tiempo_estimado_respuesta_min: int = Field(gt=0, le=720)
    tiempo_estimado_llegada_min: int | None = Field(default=None, gt=0, le=720)
    notas_taller: str | None = None


class OrdenRechazarRequest(BaseModel):
    motivo_rechazo: str = Field(min_length=3)


class AsignarMecanicoRequest(BaseModel):
    mecanico_id: UUID
    notas: str | None = None


class AsignacionEstadoRequest(BaseModel):
    estado: EstadoAsignacion
    notas: str | None = None


class AsignacionRead(BaseModel):
    id: UUID
    orden_id: UUID
    mecanico_id: UUID
    asignado_por: UUID
    estado: EstadoAsignacion
    notas: str | None
    asignado_en: datetime
    salida_en: datetime | None
    llegada_en: datetime | None
    finalizado_en: datetime | None

    model_config = {"from_attributes": True}


class HistorialEstadoOrdenRead(BaseModel):
    id: UUID
    orden_id: UUID
    estado_anterior: str | None
    estado_nuevo: str
    usuario_id: UUID | None
    observacion: str | None
    creado_en: datetime

    model_config = {"from_attributes": True}


class OrdenCancelarRequest(BaseModel):
    motivo_cancelacion: str = Field(min_length=3)


class OrdenCompletarRequest(BaseModel):
    observacion: str | None = None
