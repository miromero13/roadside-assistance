from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    CONDUCTOR = "conductor"
    TALLER = "taller"
    MECANICO = "mecanico"
    ADMIN = "admin"


class DiaSemana(str, enum.Enum):
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"


class Prioridad(str, enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class EstadoAveria(str, enum.Enum):
    REGISTRADA = "registrada"
    ANALIZANDO = "analizando"
    CLASIFICADA = "clasificada"
    PENDIENTE_ASIGNACION = "pendiente_asignacion"
    ASIGNADA = "asignada"
    EN_PROCESO = "en_proceso"
    ATENDIDA = "atendida"
    CANCELADA = "cancelada"


class MedioTipo(str, enum.Enum):
    FOTO = "foto"
    AUDIO = "audio"
    VIDEO = "video"


class ClasificacionIA(str, enum.Enum):
    BATERIA = "bateria"
    LLANTA = "llanta"
    CHOQUE = "choque"
    MOTOR = "motor"
    OTROS = "otros"
    INCIERTO = "incierto"


class EstadoOrdenServicio(str, enum.Enum):
    PENDIENTE_RESPUESTA = "pendiente_respuesta"
    ACEPTADA = "aceptada"
    RECHAZADA = "rechazada"
    TECNICO_ASIGNADO = "tecnico_asignado"
    EN_CAMINO = "en_camino"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class EstadoAsignacion(str, enum.Enum):
    ASIGNADO = "asignado"
    EN_CAMINO = "en_camino"
    ATENDIENDO = "atendiendo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class EstadoPresupuesto(str, enum.Enum):
    ENVIADO = "enviado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    VENCIDO = "vencido"


class MetodoPago(str, enum.Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    QR = "qr"


class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    REEMBOLSADO = "reembolsado"


class EstadoComision(str, enum.Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    ANULADA = "anulada"


class TipoMensaje(str, enum.Enum):
    TEXTO = "texto"
    IMAGEN = "imagen"
    AUDIO = "audio"
    SISTEMA = "sistema"


class TipoCalificador(str, enum.Enum):
    CONDUCTOR = "conductor"
    TALLER = "taller"


class TipoNotificacion(str, enum.Enum):
    ORDEN_NUEVA = "orden_nueva"
    ORDEN_ACEPTADA = "orden_aceptada"
    ORDEN_RECHAZADA = "orden_rechazada"
    ORDEN_ACTUALIZADA = "orden_actualizada"
    TECNICO_ASIGNADO = "tecnico_asignado"
    TECNICO_EN_CAMINO = "tecnico_en_camino"
    PRESUPUESTO_ENVIADO = "presupuesto_enviado"
    PRESUPUESTO_APROBADO = "presupuesto_aprobado"
    PAGO_COMPLETADO = "pago_completado"
    MENSAJE_NUEVO = "mensaje_nuevo"
    CALIFICACION_RECIBIDA = "calificacion_recibida"


class PlataformaPush(str, enum.Enum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"


class TipoCombustible(str, enum.Enum):
    GASOLINA = "gasolina"
    DIESEL = "diesel"
    ELECTRICO = "electrico"
    HIBRIDO = "hibrido"
    GAS = "gas"
