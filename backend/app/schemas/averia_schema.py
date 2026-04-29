from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi import UploadFile

from app.models.enums import EstadoAveria, MedioTipo, Prioridad
from app.schemas.catalogo_schema import CategoriaServicioRead


class AveriaCrear(BaseModel):
    vehiculo_id: UUID
    descripcion_conductor: str = Field(min_length=1)
    latitud_averia: float = Field(ge=-90, le=90)
    longitud_averia: float = Field(ge=-180, le=180)
    direccion_averia: str | None = None
    prioridad: Prioridad = Prioridad.MEDIA


class MedioAveriaCrear(BaseModel):
    tipo: MedioTipo
    url: str = Field(min_length=1)
    orden_visualizacion: int = Field(default=1, ge=1, le=20)


class MedioAveriaConArchivoCrear(BaseModel):
    tipo: MedioTipo
    orden_visualizacion: int = Field(default=1, ge=1, le=20)


class MedioAveriaRead(BaseModel):
    id: UUID
    averia_id: UUID
    tipo: MedioTipo
    url: str
    orden_visualizacion: int
    subido_en: datetime

    model_config = {"from_attributes": True}


class DiagnosticoIARead(BaseModel):
    id: UUID
    averia_id: UUID
    categoria_id: UUID | None
    categoria: CategoriaServicioRead | None = None
    clasificacion: str
    urgencia: Prioridad
    nivel_confianza: Decimal | None
    analisis: str
    resumen_automatico: str | None
    recomendacion: str | None
    danos_visibles: str | None
    costo_estimado_min: Decimal | None
    costo_estimado_max: Decimal | None
    requiere_revision_manual: bool
    generado_en: datetime

    model_config = {"from_attributes": True}


class TallerOpcionRead(BaseModel):
    """Opción de taller disponible para una avería"""

    taller_id: UUID
    nombre: str
    distancia_km: float
    tiempo_aproximado_min: int | None
    radio_cobertura_km: float
    calificacion_promedio: float
    acepta_domicilio: bool

    model_config = {"from_attributes": True}


class AveriaRead(BaseModel):
    id: UUID
    usuario_id: UUID
    vehiculo_id: UUID
    descripcion_conductor: str
    latitud_averia: float
    longitud_averia: float
    direccion_averia: str | None
    prioridad: Prioridad
    estado: EstadoAveria
    requiere_mas_informacion: bool
    creado_en: datetime
    actualizado_en: datetime
    cancelado_en: datetime | None

    model_config = {"from_attributes": True}


class AveriaDetalleRead(AveriaRead):
    medios: list[MedioAveriaRead]
    diagnostico_ia: DiagnosticoIARead | None = None
    talleres_disponibles: list[TallerOpcionRead] = Field(default_factory=list)


class ListaTalleresDisponiblesResponse(BaseModel):
    data: list[TallerOpcionRead]
    countData: int
