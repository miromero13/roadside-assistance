from pydantic import BaseModel, EmailStr


class TallerCrearPorAdmin(BaseModel):
    nombre_admin: str
    apellido_admin: str
    email_admin: EmailStr
    telefono_admin: str
    password_admin: str
    nombre_taller: str
    descripcion: str | None = None
    direccion: str
    latitud: float
    longitud: float
    radio_cobertura_km: float = 5.0
    telefono_taller: str
    foto_url: str | None = None
    acepta_domicilio: bool = False


class MecanicoCrearPorTaller(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    password: str
    especialidad: str | None = None


class CategoriaServicioCrear(BaseModel):
    nombre: str
    descripcion: str | None = None
