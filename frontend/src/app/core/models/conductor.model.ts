import { ApiResponse } from './api.model';

export type TipoCombustible = 'gasolina' | 'diesel' | 'electrico' | 'hibrido' | 'gas';
export type PrioridadAveria = 'baja' | 'media' | 'alta' | 'critica';
export type MedioTipo = 'foto' | 'video' | 'audio';

export interface Vehiculo {
  id: string;
  usuario_id: string;
  marca: string;
  modelo: string;
  anio: number;
  placa: string;
  color: string | null;
  tipo_combustible: TipoCombustible;
  foto_url: string | null;
}

export interface VehiculoPayload {
  marca: string;
  modelo: string;
  anio: number;
  placa: string;
  color?: string | null;
  tipo_combustible: TipoCombustible;
  foto_url?: string | null;
}

export interface Averia {
  id: string;
  usuario_id: string;
  vehiculo_id: string;
  descripcion_conductor: string;
  latitud_averia: number;
  longitud_averia: number;
  direccion_averia: string | null;
  prioridad: PrioridadAveria;
  estado: string;
  requiere_mas_informacion: boolean;
  creado_en: string;
  actualizado_en: string;
  cancelado_en: string | null;
}

export interface MedioAveria {
  id: string;
  averia_id: string;
  tipo: MedioTipo;
  url: string;
  orden_visualizacion: number;
  subido_en: string;
}

export interface AveriaDetalle extends Averia {
  medios: MedioAveria[];
}

export interface AveriaPayload {
  vehiculo_id: string;
  descripcion_conductor: string;
  latitud_averia: number;
  longitud_averia: number;
  direccion_averia?: string | null;
  prioridad: PrioridadAveria;
}

export interface MedioAveriaPayload {
  tipo: MedioTipo;
  url: string;
  orden_visualizacion?: number;
}

export interface CategoriaServicio {
  id: string;
  nombre: string;
  descripcion: string | null;
  activo: boolean;
}

export interface TallerCandidato {
  id: string;
  nombre: string;
  direccion: string | null;
  telefono: string | null;
  distancia_km: number;
  acepta_domicilio: boolean;
  calificacion_promedio: number | null;
}

export interface Orden {
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
  creado_en: string;
}

export interface HistorialEstadoOrden {
  id: string;
  orden_id: string;
  estado_anterior: string | null;
  estado_nuevo: string;
  usuario_id: string | null;
  observacion: string | null;
  creado_en: string;
}

export interface AsignacionOrden {
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

export interface Presupuesto {
  id: string;
  orden_id: string;
  version: number;
  descripcion_trabajos: string;
  items_detalle: { items?: Array<{ concepto?: string; cantidad?: number; precio?: number }> };
  monto_repuestos: string;
  monto_mano_obra: string;
  monto_total: string;
  estado: string;
  motivo_rechazo: string | null;
  enviado_en: string;
  respondido_en: string | null;
}

export type MetodoPago = 'efectivo' | 'tarjeta' | 'qr';

export interface Pago {
  id: string;
  orden_id: string;
  presupuesto_id: string;
  monto: string;
  metodo: MetodoPago;
  estado: string;
  referencia_externa: string | null;
  creado_en: string;
  pagado_en: string | null;
}

export interface Factura {
  id: string;
  pago_id: string;
  orden_id: string;
  numero_factura: string;
  datos_emisor: Record<string, unknown>;
  datos_receptor: Record<string, unknown>;
  items: { items?: Array<Record<string, unknown>> };
  subtotal: string;
  impuesto: string;
  total: string;
  pdf_url: string | null;
  emitida_en: string;
}

export interface Calificacion {
  id: string;
  orden_id: string;
  calificador_id: string;
  calificado_id: string;
  tipo_calificador: string;
  puntuacion: number;
  comentario: string | null;
  creado_en: string;
}

export interface Notificacion {
  id: string;
  usuario_id: string;
  orden_id: string | null;
  titulo: string;
  mensaje: string;
  tipo: string;
  leida: boolean;
  creado_en: string;
}

export type TipoMensaje = 'texto' | 'imagen' | 'audio' | 'sistema';

export interface Chat {
  id: string;
  orden_id: string;
  creado_en: string;
}

export interface MensajeChat {
  id: string;
  chat_id: string;
  remitente_id: string;
  contenido: string | null;
  tipo: TipoMensaje;
  media_url: string | null;
  leido: boolean;
  enviado_en: string;
}

export interface OrdenCrearPayload {
  averia_id: string;
  taller_id: string;
  categoria_id: string;
  es_domicilio: boolean;
  notas_conductor?: string | null;
}

export type ListResponse<T> = ApiResponse<T[]>;
