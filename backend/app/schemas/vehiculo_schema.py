from uuid import UUID

from pydantic import BaseModel

from app.models.enums import TipoCombustible


class VehiculoCrear(BaseModel):
    marca: str
    modelo: str
    anio: int
    placa: str
    color: str | None = None
    tipo_combustible: TipoCombustible
    foto_url: str | None = None


class VehiculoActualizar(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    anio: int | None = None
    placa: str | None = None
    color: str | None = None
    tipo_combustible: TipoCombustible | None = None
    foto_url: str | None = None


class VehiculoRead(BaseModel):
    id: UUID
    usuario_id: UUID
    marca: str
    modelo: str
    anio: int
    placa: str
    color: str | None
    tipo_combustible: TipoCombustible
    foto_url: str | None

    model_config = {"from_attributes": True}
