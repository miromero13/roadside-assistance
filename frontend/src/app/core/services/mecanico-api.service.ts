import { Injectable, inject } from '@angular/core';

import { ApiResponse } from '../models/api.model';
import {
  AsignacionMecanico,
  EstadoAsignacionMecanico,
  HistorialOrdenMecanico,
  ListResponse,
  OrdenMecanico,
} from '../models/mecanico.model';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class MecanicoApiService {
  private readonly api = inject(ApiService);

  listAsignacionesMias() {
    return this.api.get<ListResponse<AsignacionMecanico>>('/asignaciones/mias');
  }

  getAsignacion(asignacionId: string) {
    return this.api.get<ApiResponse<AsignacionMecanico>>(`/asignaciones/${asignacionId}`);
  }

  updateEstadoAsignacion(
    asignacionId: string,
    estado: EstadoAsignacionMecanico,
    notas?: string,
  ) {
    return this.api.put<ApiResponse<AsignacionMecanico>>(`/asignaciones/${asignacionId}/estado`, {
      estado,
      notas,
    });
  }

  getOrden(ordenId: string) {
    return this.api.get<ApiResponse<OrdenMecanico>>(`/ordenes/${ordenId}`);
  }

  listHistorialOrden(ordenId: string) {
    return this.api.get<ListResponse<HistorialOrdenMecanico>>(`/ordenes/${ordenId}/historial-estados`);
  }

  listAsignacionesOrden(ordenId: string) {
    return this.api.get<ListResponse<AsignacionMecanico>>(`/ordenes/${ordenId}/asignaciones`);
  }
}
