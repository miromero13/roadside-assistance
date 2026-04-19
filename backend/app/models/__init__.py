from app.models.averia import Averia, DiagnosticoIA, MedioAveria
from app.models.comunicacion import Calificacion, Chat, DispositivoPush, Mensaje, Notificacion
from app.models.enums import (
    ClasificacionIA,
    DiaSemana,
    EstadoAsignacion,
    EstadoAveria,
    EstadoComision,
    EstadoOrdenServicio,
    EstadoPago,
    EstadoPresupuesto,
    MedioTipo,
    MetodoPago,
    PlataformaPush,
    Prioridad,
    TipoCalificador,
    TipoCombustible,
    TipoMensaje,
    TipoNotificacion,
    UserRole,
)
from app.models.finanzas import ComisionPlataforma, Factura, Pago, Presupuesto
from app.models.orden import AsignacionOrden, HistorialEstadoOrden, MetricaServicio, OrdenServicio
from app.models.taller import BloqueoTaller, CategoriaServicio, HorarioTaller, Mecanico, ServicioTaller, Taller
from app.models.usuario import Usuario, Vehiculo
