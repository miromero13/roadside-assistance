from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, require_taller
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.gestion_schema import CategoriaServicioCrear, MecanicoCrearPorTaller, TallerCrearPorAdmin
from app.services.gestion_service import (
    crear_categoria_servicio,
    crear_mecanico_por_taller,
    crear_taller_por_admin,
)
from app.utils.response import response

router = APIRouter(prefix="/gestion", tags=["Gestión"])


@router.post("/talleres", status_code=status.HTTP_201_CREATED)
def crear_taller(
    payload: TallerCrearPorAdmin,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    try:
        usuario_taller, taller = crear_taller_por_admin(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return response(
        status_code=201,
        message="Taller creado exitosamente",
        data={
            "taller": {
                "id": str(taller.id),
                "nombre": taller.nombre,
                "direccion": taller.direccion,
                "activo": taller.activo,
            },
            "usuario_taller": {
                "id": str(usuario_taller.id),
                "nombre": usuario_taller.nombre,
                "apellido": usuario_taller.apellido,
                "email": usuario_taller.email,
                "rol": usuario_taller.rol,
            },
        },
    )


@router.post("/mecanicos", status_code=status.HTTP_201_CREATED)
def crear_mecanico(
    payload: MecanicoCrearPorTaller,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_taller),
):
    try:
        usuario_mecanico, mecanico = crear_mecanico_por_taller(db, payload, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return response(
        status_code=201,
        message="Mecánico creado exitosamente",
        data={
            "mecanico": {
                "id": str(mecanico.id),
                "taller_id": str(mecanico.taller_id),
                "especialidad": mecanico.especialidad,
                "activo": mecanico.activo,
            },
            "usuario_mecanico": {
                "id": str(usuario_mecanico.id),
                "nombre": usuario_mecanico.nombre,
                "apellido": usuario_mecanico.apellido,
                "email": usuario_mecanico.email,
                "rol": usuario_mecanico.rol,
            },
        },
    )


@router.post("/categorias-servicio", status_code=status.HTTP_201_CREATED)
def crear_categoria(
    payload: CategoriaServicioCrear,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    try:
        categoria = crear_categoria_servicio(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return response(
        status_code=201,
        message="Categoría creada exitosamente",
        data={
            "id": str(categoria.id),
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "activo": categoria.activo,
        },
    )
