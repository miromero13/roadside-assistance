from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import require_conductor
from app.core.database import get_db
from app.models.usuario import Usuario
from app.services.taller_disponibilidad_service import (
    listar_talleres_candidatos,
    obtener_averia_de_conductor,
)
from app.utils.response import response

router = APIRouter(prefix="/talleres", tags=["Selección Taller"])


@router.get("/candidatos")
def listar_talleres_candidatos_route(
    averia_id: UUID,
    categoria_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    averia = obtener_averia_de_conductor(db, averia_id, current_user.id)
    if not averia:
        raise HTTPException(status_code=404, detail="Avería no encontrada para el conductor")

    candidatos = listar_talleres_candidatos(
        db,
        float(averia.latitud_averia),
        float(averia.longitud_averia),
        categoria_id=categoria_id,
    )

    return response(
        status_code=200,
        message="Talleres candidatos obtenidos exitosamente",
        data=candidatos,
        count_data=len(candidatos),
    )
