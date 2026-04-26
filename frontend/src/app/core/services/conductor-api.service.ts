import { Injectable, inject } from '@angular/core';

import { ApiResponse } from '../models/api.model';
import {
  Averia,
  AsignacionOrden,
  AveriaDetalle,
  AveriaPayload,
  Calificacion,
  CategoriaServicio,
  Chat,
  Factura,
  HistorialEstadoOrden,
  ListResponse,
  MensajeChat,
  MetodoPago,
  MedioAveria,
  MedioAveriaPayload,
  Notificacion,
  Orden,
  OrdenCrearPayload,
  Pago,
  Presupuesto,
  TallerCandidato,
  Vehiculo,
  VehiculoPayload,
} from '../models/conductor.model';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class ConductorApiService {
  private readonly api = inject(ApiService);

  listVehiculos() {
    return this.api.get<ListResponse<Vehiculo>>('/vehiculos/');
  }

  createVehiculo(payload: VehiculoPayload) {
    return this.api.post<ApiResponse<Vehiculo>>('/vehiculos/', payload);
  }

  updateVehiculo(vehiculoId: string, payload: Partial<VehiculoPayload>) {
    return this.api.put<ApiResponse<Vehiculo>>(`/vehiculos/${vehiculoId}`, payload);
  }

  deleteVehiculo(vehiculoId: string) {
    return this.api.delete<ApiResponse<null>>(`/vehiculos/${vehiculoId}`);
  }

  listAverias() {
    return this.api.get<ListResponse<Averia>>('/averias/');
  }

  createAveria(payload: AveriaPayload) {
    return this.api.post<ApiResponse<Averia>>('/averias/', payload);
  }

  getAveria(averiaId: string) {
    return this.api.get<ApiResponse<AveriaDetalle>>(`/averias/${averiaId}`);
  }

  addAveriaMedio(averiaId: string, payload: MedioAveriaPayload) {
    return this.api.post<ApiResponse<MedioAveria>>(`/averias/${averiaId}/medios`, payload);
  }

  listCategorias() {
    return this.api.get<ListResponse<CategoriaServicio>>('/categorias-servicio');
  }

  listTalleresCandidatos(averiaId: string, categoriaId: string) {
    return this.api.get<ListResponse<TallerCandidato>>(
      `/talleres/candidatos?averia_id=${averiaId}&categoria_id=${categoriaId}`,
    );
  }

  createOrden(payload: OrdenCrearPayload) {
    return this.api.post<ApiResponse<Orden>>('/ordenes/', payload);
  }

  listOrdenes() {
    return this.api.get<ListResponse<Orden>>('/ordenes/');
  }

  getOrden(ordenId: string) {
    return this.api.get<ApiResponse<Orden>>(`/ordenes/${ordenId}`);
  }

  getOrdenHistorial(ordenId: string) {
    return this.api.get<ListResponse<HistorialEstadoOrden>>(`/ordenes/${ordenId}/historial-estados`);
  }

  getOrdenAsignaciones(ordenId: string) {
    return this.api.get<ListResponse<AsignacionOrden>>(`/ordenes/${ordenId}/asignaciones`);
  }

  getOrdenPresupuestos(ordenId: string) {
    return this.api.get<ListResponse<Presupuesto>>(`/ordenes/${ordenId}/presupuestos`);
  }

  aprobarPresupuesto(presupuestoId: string) {
    return this.api.put<ApiResponse<Presupuesto>>(`/presupuestos/${presupuestoId}/aprobar`, {});
  }

  rechazarPresupuesto(presupuestoId: string, motivo_rechazo: string) {
    return this.api.put<ApiResponse<Presupuesto>>(`/presupuestos/${presupuestoId}/rechazar`, {
      motivo_rechazo,
    });
  }

  crearPago(ordenId: string, presupuestoId: string, metodo: MetodoPago, monto: string) {
    return this.api.post<ApiResponse<Pago>>('/pagos/', {
      orden_id: ordenId,
      presupuesto_id: presupuestoId,
      metodo,
      monto: Number(monto),
    });
  }

  generarFacturaPorPago(pagoId: string) {
    return this.api.post<ApiResponse<Factura>>(`/pagos/${pagoId}/factura`, {});
  }

  getFacturaPorOrden(ordenId: string) {
    return this.api.get<ApiResponse<Factura>>(`/ordenes/${ordenId}/factura`);
  }

  crearCalificacion(ordenId: string, puntuacion: number, comentario: string) {
    return this.api.post<ApiResponse<Calificacion>>(`/ordenes/${ordenId}/calificaciones`, {
      puntuacion,
      comentario,
    });
  }

  listCalificaciones(ordenId: string) {
    return this.api.get<ListResponse<Calificacion>>(`/ordenes/${ordenId}/calificaciones`);
  }

  listNotificaciones(soloNoLeidas = false) {
    return this.api.get<ListResponse<Notificacion>>(
      `/notificaciones/?skip=0&limit=50&solo_no_leidas=${soloNoLeidas}`,
    );
  }

  marcarNotificacionLeida(notificacionId: string) {
    return this.api.put<ApiResponse<Notificacion>>(`/notificaciones/${notificacionId}/leer`, {});
  }

  marcarTodasNotificacionesLeidas() {
    return this.api.put<ApiResponse<{ total_marcadas: number }>>('/notificaciones/leer-todas', {});
  }

  getChatPorOrden(ordenId: string) {
    return this.api.get<ApiResponse<Chat>>(`/ordenes/${ordenId}/chat`);
  }

  listMensajes(chatId: string) {
    return this.api.get<ListResponse<MensajeChat>>(`/chats/${chatId}/mensajes?skip=0&limit=100`);
  }

  enviarMensaje(chatId: string, contenido: string, tipo: 'texto' | 'imagen' | 'audio' | 'sistema' = 'texto') {
    return this.api.post<ApiResponse<MensajeChat>>(`/chats/${chatId}/mensajes`, {
      contenido,
      tipo,
    });
  }

  marcarMensajeLeido(chatId: string, mensajeId: string) {
    return this.api.put<ApiResponse<MensajeChat>>(`/chats/${chatId}/mensajes/${mensajeId}/leer`, {});
  }

  marcarChatLeido(chatId: string) {
    return this.api.put<ApiResponse<{ total_marcados: number }>>(`/chats/${chatId}/leer-todo`, {});
  }

  contarNoLeidosChat(chatId: string) {
    return this.api.get<ApiResponse<{ no_leidos: number }>>(`/chats/${chatId}/no-leidos/count`);
  }

  cancelOrden(ordenId: string, motivo_cancelacion: string) {
    return this.api.put<ApiResponse<Orden>>(`/ordenes/${ordenId}/cancelar`, { motivo_cancelacion });
  }
}
