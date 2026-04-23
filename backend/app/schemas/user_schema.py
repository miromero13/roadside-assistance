from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class UsuarioCrear(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    password: str
    rol: UserRole


class UsuarioRegistroConductor(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    password: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioRead(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    rol: UserRole
    activo: bool

    model_config = {"from_attributes": True}


class UsuariosPaginadosResponse(BaseModel):
    data: List[UsuarioRead]
    countData: int


class UsuarioActualizarRol(BaseModel):
    rol: UserRole


class UsuarioActualizarPerfil(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None
    foto_url: str | None = None
    password_actual: str | None = None
    password_nueva: str | None = None


# Alias de compatibilidad temporal
UserCreate = UsuarioCrear
UserLogin = UsuarioLogin
UserRead = UsuarioRead
UserOut = UsuarioRead
UsersPaginatedResponse = UsuariosPaginadosResponse
UserUpdateType = UsuarioActualizarRol
