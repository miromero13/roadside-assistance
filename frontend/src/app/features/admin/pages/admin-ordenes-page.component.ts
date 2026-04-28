import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import {
  AdminAsignacion,
  AdminHistorialOrden,
  AdminOrden,
} from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-ordenes-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-ordenes-page.component.html',
})
export class AdminOrdenesPageComponent {
  private readonly api = inject(AdminApiService);

  protected readonly ordenes = signal<AdminOrden[]>([]);
  protected readonly filtroEstado = signal('');
  protected readonly ordenSeleccionadaId = signal<string | null>(null);
  protected readonly historial = signal<AdminHistorialOrden[]>([]);
  protected readonly asignaciones = signal<AdminAsignacion[]>([]);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.loadOrdenes();
  }

  protected async setFiltro(estado: string): Promise<void> {
    this.filtroEstado.set(estado);
    await this.loadOrdenes();
  }

  protected async verDetalle(ordenId: string): Promise<void> {
    this.errorMessage.set('');
    this.ordenSeleccionadaId.set(ordenId);
    try {
      const [historialResponse, asignacionesResponse] = await Promise.all([
        firstValueFrom(this.api.getOrdenHistorial(ordenId)),
        firstValueFrom(this.api.getOrdenAsignaciones(ordenId)),
      ]);
      this.historial.set(historialResponse.data ?? []);
      this.asignaciones.set(asignacionesResponse.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle de la orden.'));
    }
  }

  private async loadOrdenes(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listOrdenes(this.filtroEstado() || undefined));
      this.ordenes.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las órdenes.'));
    }
  }
}
