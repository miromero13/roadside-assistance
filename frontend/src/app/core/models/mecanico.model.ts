import { ApiResponse } from './api.model';

export type EstadoAsignacionMecanico =
  | 'asignado'
  | 'en_camino'
  | 'atendiendo'
  | 'finalizado'
  | 'cancelado';

export interface AsignacionMecanico {
  id: string;
  orden_id: string;
  mecanico_id: string;
  asignado_por: string;
  estado: EstadoAsignacionMecanico;
  notas: string | null;
  asignado_en: string;
  salida_en: string | null;
  llegada_en: string | null;
  finalizado_en: string | null;
}

export interface OrdenMecanico {
  id: string;
  averia_id: string;
  taller_id: string;
  categoria_id: string;
  estado: string;
  es_domicilio: boolean;
  notas_conductor: string | null;
  notas_taller: string | null;
  tiempo_estimado_respuesta_min: number | null;
  tiempo_estimado_llegada_min: number | null;
  creado_en: string;
}

export interface HistorialOrdenMecanico {
  id: string;
  orden_id: string;
  estado_anterior: string | null;
  estado_nuevo: string;
  usuario_id: string | null;
  observacion: string | null;
  creado_en: string;
}

export type ListResponse<T> = ApiResponse<T[]>;
