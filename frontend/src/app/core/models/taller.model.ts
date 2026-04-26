import { ApiResponse } from './api.model';

export interface OrdenTaller {
  id: string;
  averia_id: string;
  taller_id: string;
  categoria_id: string;
  estado: string;
  es_domicilio: boolean;
  notas_conductor: string | null;
  notas_taller: string | null;
  motivo_rechazo: string | null;
  motivo_cancelacion: string | null;
  tiempo_estimado_respuesta_min: number | null;
  tiempo_estimado_llegada_min: number | null;
  creado_en: string;
}

export interface PresupuestoTaller {
  id: string;
  orden_id: string;
  version: number;
  descripcion_trabajos: string;
  items_detalle: Record<string, unknown>;
  monto_repuestos: string;
  monto_mano_obra: string;
  monto_total: string;
  estado: string;
  motivo_rechazo: string | null;
  enviado_en: string;
  respondido_en: string | null;
}

export interface AsignacionOrdenTaller {
  id: string;
  orden_id: string;
  mecanico_id: string;
  asignado_por: string;
  estado: string;
  notas: string | null;
  asignado_en: string;
  salida_en: string | null;
  llegada_en: string | null;
  finalizado_en: string | null;
}

export interface ComisionTaller {
  id: string;
  orden_id: string;
  pago_id: string;
  monto_base: string;
  porcentaje: string;
  monto_comision: string;
  estado: string;
  creado_en: string;
  pagado_en: string | null;
}

export interface TallerInfo {
  id: string;
  usuario_id: string;
  nombre: string;
  descripcion: string | null;
  direccion: string;
  latitud: number;
  longitud: number;
  radio_cobertura_km: number;
  telefono: string;
  foto_url: string | null;
  acepta_domicilio: boolean;
  calificacion_promedio: number;
  tiempo_respuesta_promedio_min: number | null;
  activo: boolean;
}

export interface TallerServicio {
  id: string;
  taller_id: string;
  categoria_id: string;
  descripcion: string | null;
  precio_base_min: string | null;
  precio_base_max: string | null;
  tiempo_estimado_min: number | null;
  servicio_movil: boolean;
  activo: boolean;
}

export interface TallerHorario {
  id: string;
  taller_id: string;
  dia_semana: string;
  hora_apertura: string;
  hora_cierre: string;
  disponible: boolean;
}

export interface TallerBloqueo {
  id: string;
  taller_id: string;
  fecha_inicio: string;
  fecha_fin: string;
  motivo: string | null;
}

export interface MecanicoTaller {
  id: string;
  usuario_id: string;
  taller_id: string;
  especialidad: string | null;
  disponible: boolean;
  activo: boolean;
}

export type TallerListResponse<T> = ApiResponse<T[]>;
