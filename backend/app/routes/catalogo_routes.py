from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.catalogo_schema import (
    CategoriaServicioActualizarRequest,
    CategoriaServicioRead,
    ServicioTallerActualizarRequest,
    ServicioTallerCrearRequest,
    ServicioTallerRead,
)
from app.services.catalogo_service import (
    actualizar_categoria,
    actualizar_servicio_taller,
    crear_servicio_taller,
    desactivar_servicio_taller,
    listar_categorias,
    listar_servicios_taller,
    obtener_categoria,
    obtener_servicio_taller,
    obtener_taller,
)
from app.utils.response import response

router = APIRouter(tags=["Catálogo"])


@router.get("/categorias-servicio")
def listar_categorias_route(
    activo: bool | None = Query(default=True),
    db: Session = Depends(get_db),
):
    categorias = listar_categorias(db, activo=activo)
    data = [CategoriaServicioRead.model_validate(item).model_dump() for item in categorias]
    return response(
        status_code=200,
        message="Categorías obtenidas exitosamente",
        data=data,
        count_data=len(data),
    )


@router.patch("/categorias-servicio/{categoria_id}")
def actualizar_categoria_route(
    categoria_id: UUID,
    payload: CategoriaServicioActualizarRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    categoria = obtener_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No se enviaron cambios para actualizar")

    categoria = actualizar_categoria(db, categoria, data)
    result = CategoriaServicioRead.model_validate(categoria).model_dump()
    return response(status_code=200, message="Categoría actualizada exitosamente", data=result)


@router.post("/talleres/{taller_id}/servicios", status_code=status.HTTP_201_CREATED)
def crear_servicio_taller_route(
    taller_id: UUID,
    payload: ServicioTallerCrearRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    categoria = obtener_categoria(db, payload.categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    try:
        servicio = crear_servicio_taller(
            db,
            taller,
            categoria,
            current_user,
            payload.model_dump(),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = ServicioTallerRead.model_validate(servicio).model_dump()
    return response(status_code=201, message="Servicio de taller creado exitosamente", data=data)


@router.get("/talleres/{taller_id}/servicios")
def listar_servicios_taller_route(
    taller_id: UUID,
    solo_activos: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    taller = obtener_taller(db, taller_id)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    servicios = listar_servicios_taller(db, taller_id=taller_id, solo_activos=solo_activos)
    data = [ServicioTallerRead.model_validate(item).model_dump() for item in servicios]
    return response(
        status_code=200,
        message="Servicios de taller obtenidos exitosamente",
        data=data,
        count_data=len(data),
    )


@router.patch("/servicios-taller/{servicio_id}")
def actualizar_servicio_taller_route(
    servicio_id: UUID,
    payload: ServicioTallerActualizarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    servicio = obtener_servicio_taller(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio de taller no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No se enviaron cambios para actualizar")

    try:
        servicio = actualizar_servicio_taller(db, servicio, current_user, data)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = ServicioTallerRead.model_validate(servicio).model_dump()
    return response(status_code=200, message="Servicio de taller actualizado exitosamente", data=result)


@router.delete("/servicios-taller/{servicio_id}")
def eliminar_servicio_taller_route(
    servicio_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    servicio = obtener_servicio_taller(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio de taller no encontrado")

    try:
        servicio = desactivar_servicio_taller(db, servicio, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = ServicioTallerRead.model_validate(servicio).model_dump()
    return response(status_code=200, message="Servicio de taller desactivado exitosamente", data=result)
