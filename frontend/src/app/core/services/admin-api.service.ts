import { Injectable, inject } from '@angular/core';

import { ApiResponse } from '../models/api.model';
import {
  AdminAveria,
  AdminAsignacion,
  AdminCategoriaServicio,
  AdminComision,
  AdminFactura,
  AdminHistorialOrden,
  AdminMecanico,
  AdminMetrica,
  AdminOrden,
  AdminPago,
  AdminTaller,
  AdminServicioTaller,
  AdminUsuario,
  ListResponse,
} from '../models/admin.model';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly api = inject(ApiService);

  listUsuarios(skip = 0, limit = 100) {
    return this.api.get<ListResponse<AdminUsuario>>(`/users/?skip=${skip}&limit=${limit}`);
  }

  updateUsuarioRol(userId: string, rol: AdminUsuario['rol']) {
    return this.api.patch<ApiResponse<AdminUsuario>>(`/users/${userId}/rol`, { rol });
  }

  listOrdenes(estado?: string) {
    const query = estado ? `?estado=${estado}` : '';
    return this.api.get<ListResponse<AdminOrden>>(`/ordenes/${query}`);
  }

  getOrden(ordenId: string) {
    return this.api.get<ApiResponse<AdminOrden>>(`/ordenes/${ordenId}`);
  }

  getAveria(averiaId: string) {
    return this.api.get<ApiResponse<AdminAveria>>(`/averias/${averiaId}`);
  }

  getOrdenHistorial(ordenId: string) {
    return this.api.get<ListResponse<AdminHistorialOrden>>(`/ordenes/${ordenId}/historial-estados`);
  }

  getOrdenAsignaciones(ordenId: string) {
    return this.api.get<ListResponse<AdminAsignacion>>(`/ordenes/${ordenId}/asignaciones`);
  }

  listTalleres() {
    return this.api.get<ListResponse<AdminTaller>>('/operaciones/talleres');
  }

  getTaller(tallerId: string) {
    return this.api.get<ApiResponse<AdminTaller>>(`/talleres/${tallerId}`);
  }

  listMecanicos(disponible?: boolean) {
    const query = disponible === undefined ? '' : `?disponible=${disponible}`;
    return this.api.get<ListResponse<AdminMecanico>>(`/operaciones/mecanicos${query}`);
  }

  listMecanicosPorTaller(tallerId: string, disponible?: boolean) {
    const query = disponible === undefined ? '' : `?disponible=${disponible}`;
    return this.api.get<ListResponse<AdminMecanico>>(`/operaciones/talleres/${tallerId}/mecanicos${query}`);
  }

  updateMecanicoDisponibilidad(mecanicoId: string, disponible: boolean) {
    return this.api.patch<ApiResponse<{ id: string; disponible: boolean }>>(
      `/mecanicos/${mecanicoId}/disponibilidad`,
      { disponible },
    );
  }

  listCategorias(activo?: boolean) {
    const query = activo === undefined ? '' : `?activo=${activo}`;
    return this.api.get<ListResponse<AdminCategoriaServicio>>(`/categorias-servicio${query}`);
  }

  createCategoria(nombre: string, descripcion: string | null) {
    return this.api.post<ApiResponse<AdminCategoriaServicio>>('/gestion/categorias-servicio', {
      nombre,
      descripcion,
    });
  }

  updateCategoria(
    categoriaId: string,
    payload: Partial<Pick<AdminCategoriaServicio, 'nombre' | 'descripcion' | 'activo'>>,
  ) {
    return this.api.patch<ApiResponse<AdminCategoriaServicio>>(
      `/categorias-servicio/${categoriaId}`,
      payload,
    );
  }

  listServiciosTaller(tallerId: string, soloActivos = false) {
    return this.api.get<ListResponse<AdminServicioTaller>>(
      `/talleres/${tallerId}/servicios?solo_activos=${soloActivos}`,
    );
  }

  listPagos(params?: {
    estado?: string;
    metodo?: string;
    orden_id?: string;
    creado_desde?: string;
    creado_hasta?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.estado) query.set('estado', params.estado);
    if (params?.metodo) query.set('metodo', params.metodo);
    if (params?.orden_id) query.set('orden_id', params.orden_id);
    if (params?.creado_desde) query.set('creado_desde', params.creado_desde);
    if (params?.creado_hasta) query.set('creado_hasta', params.creado_hasta);
    query.set('skip', '0');
    query.set('limit', '100');
    return this.api.get<ListResponse<AdminPago>>(`/pagos/?${query.toString()}`);
  }

  listComisiones(params?: {
    estado?: string;
    orden_id?: string;
    pago_id?: string;
    creado_desde?: string;
    creado_hasta?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.estado) query.set('estado', params.estado);
    if (params?.orden_id) query.set('orden_id', params.orden_id);
    if (params?.pago_id) query.set('pago_id', params.pago_id);
    if (params?.creado_desde) query.set('creado_desde', params.creado_desde);
    if (params?.creado_hasta) query.set('creado_hasta', params.creado_hasta);
    query.set('skip', '0');
    query.set('limit', '100');
    return this.api.get<ListResponse<AdminComision>>(`/comisiones/?${query.toString()}`);
  }

  listFacturas(params?: {
    orden_id?: string;
    pago_id?: string;
    emitida_desde?: string;
    emitida_hasta?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.orden_id) query.set('orden_id', params.orden_id);
    if (params?.pago_id) query.set('pago_id', params.pago_id);
    if (params?.emitida_desde) query.set('emitida_desde', params.emitida_desde);
    if (params?.emitida_hasta) query.set('emitida_hasta', params.emitida_hasta);
    query.set('skip', '0');
    query.set('limit', '100');
    return this.api.get<ListResponse<AdminFactura>>(`/facturas?${query.toString()}`);
  }

  listMetricas(params?: {
    orden_id?: string;
    creado_desde?: string;
    creado_hasta?: string;
    calificacion_min?: string;
    calificacion_max?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.orden_id) query.set('orden_id', params.orden_id);
    if (params?.creado_desde) query.set('creado_desde', params.creado_desde);
    if (params?.creado_hasta) query.set('creado_hasta', params.creado_hasta);
    if (params?.calificacion_min) query.set('calificacion_min', params.calificacion_min);
    if (params?.calificacion_max) query.set('calificacion_max', params.calificacion_max);
    query.set('skip', '0');
    query.set('limit', '100');
    return this.api.get<ListResponse<AdminMetrica>>(`/metricas/ordenes?${query.toString()}`);
  }

  recalcularMetricaOrden(ordenId: string) {
    return this.api.post<ApiResponse<AdminMetrica>>(`/metricas/ordenes/${ordenId}/recalcular`, {});
  }
}
