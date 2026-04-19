from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user, require_conductor
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.usuario import Usuario
from app.schemas.vehiculo_schema import VehiculoActualizar, VehiculoCrear, VehiculoRead
from app.services.vehiculo_service import (
    actualizar_vehiculo,
    crear_vehiculo,
    eliminar_vehiculo,
    listar_vehiculos_por_usuario,
    obtener_vehiculo_por_id,
)
from app.utils.response import response

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_vehiculo_route(
    payload: VehiculoCrear,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    try:
        vehiculo = crear_vehiculo(db, payload, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = VehiculoRead.model_validate(vehiculo).model_dump()
    return response(status_code=201, message="Vehículo creado exitosamente", data=data)


@router.get("/")
def listar_vehiculos_route(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    vehiculos = listar_vehiculos_por_usuario(db, current_user.id)
    data = [VehiculoRead.model_validate(item).model_dump() for item in vehiculos]
    return response(
        status_code=200,
        message="Vehículos obtenidos exitosamente",
        data=data,
        count_data=len(data),
    )


@router.get("/{vehiculo_id}")
def obtener_vehiculo_route(
    vehiculo_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    vehiculo = obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if current_user.rol != UserRole.ADMIN and vehiculo.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este vehículo")

    data = VehiculoRead.model_validate(vehiculo).model_dump()
    return response(status_code=200, message="Vehículo obtenido exitosamente", data=data)


@router.put("/{vehiculo_id}")
def actualizar_vehiculo_route(
    vehiculo_id: UUID,
    payload: VehiculoActualizar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    vehiculo = obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if vehiculo.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este vehículo")

    try:
        vehiculo = actualizar_vehiculo(db, vehiculo, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = VehiculoRead.model_validate(vehiculo).model_dump()
    return response(status_code=200, message="Vehículo actualizado exitosamente", data=data)


@router.delete("/{vehiculo_id}")
def eliminar_vehiculo_route(
    vehiculo_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    vehiculo = obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if vehiculo.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este vehículo")

    try:
        eliminar_vehiculo(db, vehiculo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return response(status_code=200, message="Vehículo eliminado exitosamente")
