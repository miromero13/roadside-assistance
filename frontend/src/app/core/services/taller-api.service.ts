import { Injectable, inject } from '@angular/core';

import { ApiResponse } from '../models/api.model';
import {
  AsignacionOrdenTaller,
  ComisionTaller,
  MecanicoTaller,
  OrdenTaller,
  PresupuestoTaller,
  TallerInfo,
  TallerBloqueo,
  TallerHorario,
  TallerServicio,
  TallerListResponse,
} from '../models/taller.model';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class TallerApiService {
  private readonly api = inject(ApiService);

  listOrdenes(estado?: string) {
    const query = estado ? `?estado=${estado}` : '';
    return this.api.get<TallerListResponse<OrdenTaller>>(`/ordenes/${query}`);
  }

  getOrden(ordenId: string) {
    return this.api.get<ApiResponse<OrdenTaller>>(`/ordenes/${ordenId}`);
  }

  aceptarOrden(ordenId: string, payload: { tiempo_estimado_respuesta_min: number; tiempo_estimado_llegada_min?: number | null; notas_taller?: string | null; }) {
    return this.api.put<ApiResponse<OrdenTaller>>(`/ordenes/${ordenId}/aceptar`, payload);
  }

  rechazarOrden(ordenId: string, motivo_rechazo: string) {
    return this.api.put<ApiResponse<OrdenTaller>>(`/ordenes/${ordenId}/rechazar`, { motivo_rechazo });
  }

  asignarMecanico(ordenId: string, mecanico_id: string, notas: string) {
    return this.api.post<ApiResponse<AsignacionOrdenTaller>>(`/ordenes/${ordenId}/asignar-mecanico`, {
      mecanico_id,
      notas,
    });
  }

  listAsignaciones(ordenId: string) {
    return this.api.get<TallerListResponse<AsignacionOrdenTaller>>(`/ordenes/${ordenId}/asignaciones`);
  }

  listMecanicos(disponible?: boolean) {
    const query = disponible === undefined ? '' : `?disponible=${disponible}`;
    return this.api.get<TallerListResponse<MecanicoTaller>>(`/operaciones/mecanicos${query}`);
  }

  listPresupuestos(ordenId: string) {
    return this.api.get<TallerListResponse<PresupuestoTaller>>(`/ordenes/${ordenId}/presupuestos`);
  }

  crearPresupuesto(
    ordenId: string,
    payload: {
      descripcion_trabajos: string;
      items_detalle: Record<string, unknown>;
      monto_repuestos: number;
      monto_mano_obra: number;
    },
  ) {
    return this.api.post<ApiResponse<PresupuestoTaller>>(`/ordenes/${ordenId}/presupuestos`, payload);
  }

  listComisionesMias() {
    return this.api.get<TallerListResponse<ComisionTaller>>('/comisiones/mias?skip=0&limit=100');
  }

  listNotificaciones(soloNoLeidas = false) {
    return this.api.get<TallerListResponse<{
      id: string;
      usuario_id: string;
      orden_id: string | null;
      titulo: string;
      mensaje: string;
      tipo: string;
      leida: boolean;
      creado_en: string;
    }>>(`/notificaciones/?skip=0&limit=50&solo_no_leidas=${soloNoLeidas}`);
  }

  marcarNotificacionLeida(notificacionId: string) {
    return this.api.put<ApiResponse<null>>(`/notificaciones/${notificacionId}/leer`, {});
  }

  marcarTodasNotificacionesLeidas() {
    return this.api.put<ApiResponse<{ total_marcadas: number }>>('/notificaciones/leer-todas', {});
  }

  getChatPorOrden(ordenId: string) {
    return this.api.get<ApiResponse<{ id: string; orden_id: string; creado_en: string }>>(`/ordenes/${ordenId}/chat`);
  }

  listMensajes(chatId: string) {
    return this.api.get<TallerListResponse<{
      id: string;
      chat_id: string;
      remitente_id: string;
      contenido: string | null;
      tipo: string;
      media_url: string | null;
      leido: boolean;
      enviado_en: string;
    }>>(`/chats/${chatId}/mensajes?skip=0&limit=100`);
  }

  enviarMensaje(chatId: string, contenido: string) {
    return this.api.post<ApiResponse<null>>(`/chats/${chatId}/mensajes`, { contenido, tipo: 'texto' });
  }

  marcarMensajeLeido(chatId: string, mensajeId: string) {
    return this.api.put<ApiResponse<null>>(`/chats/${chatId}/mensajes/${mensajeId}/leer`, {});
  }

  marcarChatLeido(chatId: string) {
    return this.api.put<ApiResponse<{ total_marcados: number }>>(`/chats/${chatId}/leer-todo`, {});
  }

  contarNoLeidosChat(chatId: string) {
    return this.api.get<ApiResponse<{ no_leidos: number }>>(`/chats/${chatId}/no-leidos/count`);
  }

  pagarComision(comisionId: string) {
    return this.api.post<ApiResponse<ComisionTaller>>(`/comisiones/${comisionId}/pagar`, {});
  }

  getTaller(tallerId: string) {
    return this.api.get<ApiResponse<TallerInfo>>(`/talleres/${tallerId}`);
  }

  getMiTaller() {
    return this.api.get<ApiResponse<TallerInfo>>('/operaciones/taller/mio');
  }

  updateTaller(tallerId: string, payload: Partial<TallerInfo>) {
    return this.api.patch<ApiResponse<TallerInfo>>(`/talleres/${tallerId}`, payload);
  }

  listCategorias() {
    return this.api.get<TallerListResponse<{ id: string; nombre: string; descripcion: string | null; activo: boolean }>>(
      '/categorias-servicio?activo=true',
    );
  }

  listServicios(tallerId: string) {
    return this.api.get<TallerListResponse<TallerServicio>>(`/talleres/${tallerId}/servicios?solo_activos=false`);
  }

  createServicio(tallerId: string, payload: {
    categoria_id: string;
    descripcion?: string | null;
    precio_base_min?: number | null;
    precio_base_max?: number | null;
    tiempo_estimado_min?: number | null;
    servicio_movil: boolean;
  }) {
    return this.api.post<ApiResponse<TallerServicio>>(`/talleres/${tallerId}/servicios`, payload);
  }

  updateServicio(servicioId: string, payload: Partial<TallerServicio>) {
    return this.api.patch<ApiResponse<TallerServicio>>(`/servicios-taller/${servicioId}`, payload);
  }

  deleteServicio(servicioId: string) {
    return this.api.delete<ApiResponse<null>>(`/servicios-taller/${servicioId}`);
  }

  listHorarios(tallerId: string) {
    return this.api.get<TallerListResponse<TallerHorario>>(`/talleres/${tallerId}/horarios`);
  }

  createHorario(tallerId: string, payload: {
    dia_semana: string;
    hora_apertura: string;
    hora_cierre: string;
    disponible: boolean;
  }) {
    return this.api.post<ApiResponse<TallerHorario>>(`/talleres/${tallerId}/horarios`, payload);
  }

  updateHorario(tallerId: string, horarioId: string, payload: Partial<TallerHorario>) {
    return this.api.patch<ApiResponse<TallerHorario>>(`/talleres/${tallerId}/horarios/${horarioId}`, payload);
  }

  deleteHorario(tallerId: string, horarioId: string) {
    return this.api.delete<ApiResponse<null>>(`/talleres/${tallerId}/horarios/${horarioId}`);
  }

  listBloqueos(tallerId: string) {
    return this.api.get<TallerListResponse<TallerBloqueo>>(`/talleres/${tallerId}/bloqueos`);
  }

  createBloqueo(tallerId: string, payload: {
    fecha_inicio: string;
    fecha_fin: string;
    motivo?: string | null;
  }) {
    return this.api.post<ApiResponse<TallerBloqueo>>(`/talleres/${tallerId}/bloqueos`, payload);
  }

  deleteBloqueo(tallerId: string, bloqueoId: string) {
    return this.api.delete<ApiResponse<null>>(`/talleres/${tallerId}/bloqueos/${bloqueoId}`);
  }
}
