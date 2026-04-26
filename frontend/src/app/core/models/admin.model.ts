import { ApiResponse } from './api.model';

export interface AdminUsuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
  rol: 'conductor' | 'taller' | 'mecanico' | 'admin';
  activo: boolean;
}

export interface AdminOrden {
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

export interface AdminHistorialOrden {
  id: string;
  orden_id: string;
  estado_anterior: string | null;
  estado_nuevo: string;
  usuario_id: string | null;
  observacion: string | null;
  creado_en: string;
}

export interface AdminAsignacion {
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

export interface AdminPago {
  id: string;
  orden_id: string;
  presupuesto_id: string | null;
  monto: string;
  metodo: string;
  estado: string;
  referencia_externa: string | null;
  pagado_en: string | null;
  creado_en: string;
}

export interface AdminComision {
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

export interface AdminFactura {
  id: string;
  pago_id: string;
  orden_id: string;
  numero_factura: string;
  subtotal: string;
  impuesto: string;
  total: string;
  pdf_url: string | null;
  emitida_en: string;
}

export interface AdminMetrica {
  id: string;
  orden_id: string;
  tiempo_respuesta_min: number | null;
  tiempo_llegada_min: number | null;
  tiempo_resolucion_min: number | null;
  calificacion_final: string | null;
  creado_en: string;
}

export interface AdminCategoriaServicio {
  id: string;
  nombre: string;
  descripcion: string | null;
  activo: boolean;
}

export interface AdminMecanico {
  id: string;
  usuario_id: string;
  taller_id: string;
  especialidad: string | null;
  disponible: boolean;
  activo: boolean;
}

export interface AdminServicioTaller {
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

export type ListResponse<T> = ApiResponse<T[]>;
