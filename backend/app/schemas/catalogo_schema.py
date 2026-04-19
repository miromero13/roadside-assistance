from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CategoriaServicioRead(BaseModel):
    id: UUID
    nombre: str
    descripcion: str | None
    activo: bool

    model_config = {"from_attributes": True}


class CategoriaServicioActualizarRequest(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    activo: bool | None = None


class ServicioTallerCrearRequest(BaseModel):
    categoria_id: UUID
    descripcion: str | None = None
    precio_base_min: Decimal | None = Field(default=None, ge=0)
    precio_base_max: Decimal | None = Field(default=None, ge=0)
    tiempo_estimado_min: int | None = Field(default=None, gt=0)
    servicio_movil: bool = False


class ServicioTallerActualizarRequest(BaseModel):
    descripcion: str | None = None
    precio_base_min: Decimal | None = Field(default=None, ge=0)
    precio_base_max: Decimal | None = Field(default=None, ge=0)
    tiempo_estimado_min: int | None = Field(default=None, gt=0)
    servicio_movil: bool | None = None
    activo: bool | None = None


class ServicioTallerRead(BaseModel):
    id: UUID
    taller_id: UUID
    categoria_id: UUID
    descripcion: str | None
    precio_base_min: Decimal | None
    precio_base_max: Decimal | None
    tiempo_estimado_min: int | None
    servicio_movil: bool
    activo: bool

    model_config = {"from_attributes": True}
