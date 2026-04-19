from enum import Enum


class RolUsuarioEnum(str, Enum):
    conductor = "conductor"
    taller = "taller"
    mecanico = "mecanico"
    admin = "admin"


# Alias de compatibilidad temporal
UserTypeEnum = RolUsuarioEnum
